"""PostgreSQL + pgvector persistence: chunks, page registry, watermark, dead letters.

All statements are in ``confluence_indexer/sql``; this module only binds
parameters, manages transactions and shapes results.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from datetime import datetime
from typing import Any

import numpy as np
import psycopg
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row

from ..models import IndexedPage, PageDocument
from ..sql import migrations, query

log = logging.getLogger(__name__)

_DIMENSIONS_VAR = re.compile(r":embedding_dimensions\b")


class SchemaMismatchError(RuntimeError):
    pass


class PgVectorStore:
    """Holds one connection for the lifetime of a pipeline stage.

    The connection runs in autocommit mode; every multi-statement write is
    wrapped in an explicit transaction so a page's rows change atomically.
    """

    def __init__(self, conn: psycopg.Connection[Any]) -> None:
        self._conn = conn

    @classmethod
    @contextmanager
    def connect(cls, dsn: str) -> Iterator[PgVectorStore]:
        with psycopg.connect(
            dsn, autocommit=True, row_factory=dict_row, application_name="confluence-indexer"
        ) as conn:
            register_vector(conn)
            yield cls(conn)

    # -- schema ------------------------------------------------------------

    def check_schema(self, dimensions: int) -> None:
        row = self._one("check_embedding_column")
        expected = f"vector({dimensions})"
        if row is None or row["column_type"] != expected:
            found = row["column_type"] if row else "missing"
            raise SchemaMismatchError(
                f"chunks.embedding is {found}, but EMBEDDING_DIMENSIONS needs {expected}"
            )

    # -- watermark ---------------------------------------------------------

    def get_watermark(self, pipeline: str) -> datetime | None:
        row = self._one("get_watermark", pipeline_name=pipeline)
        return row["watermark"] if row else None

    def advance_watermark(self, pipeline: str, watermark: datetime, run_id: str) -> datetime:
        row = self._one(
            "advance_watermark", pipeline_name=pipeline, watermark=watermark, run_id=run_id
        )
        assert row is not None
        stored: datetime = row["watermark"]
        return stored

    # -- page state --------------------------------------------------------

    def get_indexed_pages(self, page_ids: Sequence[str]) -> dict[str, IndexedPage]:
        if not page_ids:
            return {}
        rows = self._all("get_indexed_pages", page_ids=list(page_ids))
        return {r["page_id"]: IndexedPage(**r) for r in rows}

    def find_embeddings(
        self, content_hashes: Iterable[str], embedding_version: str
    ) -> dict[str, np.ndarray]:
        hashes = list(set(content_hashes))
        if not hashes:
            return {}
        rows = self._all(
            "find_embeddings", content_hashes=hashes, embedding_version=embedding_version
        )
        return {r["content_hash"]: r["embedding"] for r in rows}

    def upsert_page(
        self,
        document: PageDocument,
        vectors: Mapping[str, Sequence[float] | np.ndarray],
        embedding_version: str,
    ) -> int:
        """Replace a page's rows atomically. Returns the number of chunks removed."""
        meta = document.metadata
        with self._conn.transaction(), self._conn.cursor() as cur:
            cur.execute(
                query("upsert_page"),
                {
                    **meta.to_dict(),
                    "last_modified": meta.last_modified,
                    "content_hash": document.content_hash,
                    "embedding_version": embedding_version,
                    "chunk_count": len(document.chunks),
                    "raw_uri": document.raw_uri,
                },
            )
            if document.chunks:
                cur.executemany(
                    query("upsert_chunk"),
                    [
                        {
                            "chunk_id": chunk.chunk_id,
                            "page_id": chunk.page_id,
                            "chunk_index": chunk.chunk_index,
                            "content": chunk.text,
                            "embedding_text": chunk.embedding_text,
                            "content_hash": chunk.content_hash,
                            "token_count": chunk.token_count,
                            "embedding_version": embedding_version,
                            "embedding": np.asarray(vectors[chunk.content_hash]),
                            "metadata": json.dumps(chunk_metadata(document, chunk.chunk_index)),
                        }
                        for chunk in document.chunks
                    ],
                )
            cur.execute(
                query("delete_trailing_chunks"),
                {"page_id": meta.page_id, "chunk_count": len(document.chunks)},
            )
            return cur.rowcount

    def touch_page(self, document: PageDocument) -> None:
        meta = document.metadata
        self._execute(
            "touch_page",
            page_id=meta.page_id,
            version=meta.version,
            last_modified=meta.last_modified,
            last_modified_by=meta.last_modified_by,
            raw_uri=document.raw_uri,
        )

    # -- deletions ---------------------------------------------------------

    def list_active_page_ids(self, indexed_before: datetime) -> set[str]:
        rows = self._all("list_active_page_ids", indexed_before=indexed_before)
        return {r["page_id"] for r in rows}

    def count_active_pages(self) -> int:
        row = self._one("count_active_pages")
        return int(row["n"]) if row else 0

    def mark_pages_deleted(self, page_ids: Iterable[str]) -> tuple[int, int]:
        """Remove chunks (and so vectors) and soft-delete pages. Returns (pages, chunks)."""
        ids = list(page_ids)
        if not ids:
            return 0, 0
        params = {"page_ids": ids}
        with self._conn.transaction(), self._conn.cursor() as cur:
            cur.execute(query("delete_page_chunks"), params)
            chunks = cur.rowcount
            cur.execute(query("soft_delete_pages"), params)
            pages = cur.rowcount
            cur.execute(query("clear_failures"), params)
        return pages, chunks

    # -- dead letters ------------------------------------------------------

    def record_failure(self, page_id: str, stage: str, error: BaseException, run_id: str) -> None:
        self._execute(
            "record_failure",
            page_id=page_id,
            stage=stage,
            error=f"{type(error).__name__}: {error}"[:4000],
            run_id=run_id,
        )

    def clear_failures(self, page_ids: Iterable[str]) -> None:
        ids = list(page_ids)
        if ids:
            self._execute("clear_failures", page_ids=ids)

    def retryable_failures(self, max_attempts: int) -> list[str]:
        return [r["page_id"] for r in self._all("retryable_failures", max_attempts=max_attempts)]

    def count_parked_failures(self, max_attempts: int) -> int:
        row = self._one("count_parked_failures", max_attempts=max_attempts)
        return int(row["n"]) if row else 0

    # -- run audit ---------------------------------------------------------

    def record_run(
        self,
        pipeline: str,
        run_id: str,
        status: str,
        stats: Mapping[str, Any],
        failed_stages: Sequence[str],
    ) -> None:
        self._execute(
            "record_run",
            run_id=run_id,
            pipeline_name=pipeline,
            status=status,
            stats=json.dumps(stats),
            failed_stages=list(failed_stages),
        )

    # -- helpers -----------------------------------------------------------

    def _execute(self, name: str, **params: Any) -> None:
        with self._conn.cursor() as cur:
            cur.execute(query(name), params)

    def _one(self, name: str, **params: Any) -> dict[str, Any] | None:
        with self._conn.cursor() as cur:
            cur.execute(query(name), params)
            row: dict[str, Any] | None = cur.fetchone()
            return row

    def _all(self, name: str, **params: Any) -> list[dict[str, Any]]:
        with self._conn.cursor() as cur:
            cur.execute(query(name), params)
            rows: list[dict[str, Any]] = cur.fetchall()
            return rows


def chunk_metadata(document: PageDocument, chunk_index: int) -> dict[str, Any]:
    """Filterable source metadata stored with each chunk.

    Volatile fields (version, last_modified, chunk_count) live on the pages
    table only, so a save that changes nothing indexable, or a chunk added at
    the end of a page, does not rewrite every chunk row.
    """
    meta = document.metadata
    chunk = document.chunks[chunk_index]
    return {
        "source": "confluence",
        "page_id": meta.page_id,
        "space_key": meta.space_key,
        "space_name": meta.space_name,
        "title": meta.title,
        "url": meta.url,
        "labels": list(meta.labels),
        "ancestors": list(meta.ancestors),
        "section": list(chunk.section),
        "chunk_index": chunk_index,
    }


def apply_migrations(dsn: str, embedding_dimensions: int) -> list[str]:
    """Apply pending migrations once each, in order. Returns the files applied.

    ``:embedding_dimensions`` in a migration is replaced with the configured
    vector size, the same variable ``psql -v embedding_dimensions=N`` would set.
    """
    applied: list[str] = []
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute(query("migrations_create_table"))
        conn.execute(query("migrations_lock"))
        try:
            done = {row[0] for row in conn.execute(query("migrations_applied"))}
            for migration in migrations():
                if migration.name in done:
                    continue
                log.info("Applying migration %s", migration.name)
                ddl = _DIMENSIONS_VAR.sub(str(int(embedding_dimensions)), migration.read_text())
                with conn.transaction():
                    conn.execute(ddl.encode())
                    conn.execute(query("migrations_record"), {"name": migration.name})
                applied.append(migration.name)
        finally:
            conn.execute(query("migrations_unlock"))
    return applied
