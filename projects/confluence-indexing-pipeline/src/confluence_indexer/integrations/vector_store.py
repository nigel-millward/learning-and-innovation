"""PostgreSQL + pgvector persistence: chunks, page registry, load_date, dead letters.

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
from ..sql import query, schema_management

log = logging.getLogger(__name__)

_DIMENSIONS_VAR = re.compile(r":embedding_dimensions\b")


class SchemaMismatchError(RuntimeError):
    """Raised when the database schema does not match the configuration."""


class PgVectorStore:
    """Holds one connection for the lifetime of a pipeline stage.

    The connection runs in autocommit mode; every multi-statement write is
    wrapped in an explicit transaction so a page's rows change atomically.
    """

    def __init__(self, conn: psycopg.Connection[Any]) -> None:
        """Wrap an open connection.

        Args:
            conn: Autocommit connection with ``dict_row`` rows and pgvector types
                registered, as opened by ``connect``.
        """
        self._conn = conn

    @classmethod
    @contextmanager
    def connect(cls, database_connection_string: str) -> Iterator[PgVectorStore]:
        """Open a connection and yield a store that uses it; close it on exit.

        Args:
            database_connection_string: libpq connection URI.

        Yields:
            The store.
        """
        with psycopg.connect(
            database_connection_string,
            autocommit=True,
            row_factory=dict_row,
            application_name="confluence-indexer",
        ) as conn:
            register_vector(conn)
            yield cls(conn)

    # -- schema ------------------------------------------------------------

    def check_schema(self, dimensions: int) -> None:
        """Check that ``chunks.embedding`` has the configured vector size.

        Args:
            dimensions: Configured embedding dimensions.

        Raises:
            SchemaMismatchError: If the column is missing or has another size.
        """
        row = self._one("check_embedding_column")
        expected = f"vector({dimensions})"
        if row is None or row["column_type"] != expected:
            found = row["column_type"] if row else "missing"
            raise SchemaMismatchError(
                f"chunks.embedding is {found}, but EMBEDDING_DIMENSIONS needs {expected}"
            )

    # -- load_date ---------------------------------------------------------

    def get_load_date(self, pipeline: str) -> datetime | None:
        """Return the stored load_date for a pipeline.

        Args:
            pipeline: Pipeline name.

        Returns:
            The load_date, or None before the first successful run.
        """
        row = self._one("get_watermark", pipeline_name=pipeline)
        return row["load_date"] if row else None

    def advance_load_date(self, pipeline: str, load_date: datetime, run_id: str) -> datetime:
        """Move the load_date forward to ``load_date``; it is never moved back.

        Args:
            pipeline: Pipeline name.
            load_date: Proposed new load_date.
            run_id: Airflow run ID, recorded as the last run.

        Returns:
            The stored load_date: the later of the current and proposed values.
        """
        row = self._one(
            "advance_watermark", pipeline_name=pipeline, load_date=load_date, run_id=run_id
        )
        assert row is not None
        stored: datetime = row["load_date"]
        return stored

    # -- page state --------------------------------------------------------

    def get_indexed_pages(self, page_ids: Sequence[str]) -> dict[str, IndexedPage]:
        """Return what the index holds for the given pages.

        Args:
            page_ids: Confluence content IDs.

        Returns:
            Page ID to its indexed state, for active pages only.
        """
        if not page_ids:
            return {}
        rows = self._all("get_indexed_pages", page_ids=list(page_ids))
        return {r["page_id"]: IndexedPage(**r) for r in rows}

    def find_embeddings(
        self, content_hashes: Iterable[str], embedding_version: str
    ) -> dict[str, np.ndarray]:
        """Find existing vectors for chunk hashes, from any page.

        Unchanged, moved or duplicated text is never sent to the embedding model twice.

        Args:
            content_hashes: Chunk content hashes to look up; duplicates are ignored.
            embedding_version: Embedding space the vectors must belong to.

        Returns:
            Content hash to vector, for the hashes that were found.
        """
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
        """Replace a page's rows atomically.

        Upserts the page row and every chunk, then deletes chunks beyond the
        page's new length, all in one transaction.

        Args:
            document: Page and chunks to write.
            vectors: Content hash to vector; must hold every chunk's hash.
            embedding_version: Embedding space of the vectors.

        Returns:
            The number of trailing chunks removed because the page got shorter.
        """
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
        """Record a new Confluence version whose indexed content is unchanged.

        Updates only the version, modification fields and raw URI; chunks are untouched.

        Args:
            document: The page's new version.
        """
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
        """Return active pages indexed before a given time.

        Args:
            indexed_before: Exclusive upper bound on ``indexed_at``.

        Returns:
            The page IDs.
        """
        rows = self._all("list_active_page_ids", indexed_before=indexed_before)
        return {r["page_id"] for r in rows}

    def count_active_pages(self) -> int:
        """Return the number of active pages in the index.

        Returns:
            The count.
        """
        row = self._one("count_active_pages")
        return int(row["n"]) if row else 0

    def mark_pages_deleted(self, page_ids: Iterable[str]) -> tuple[int, int]:
        """Remove chunks (and so vectors) and soft-delete pages, in one transaction.

        Pages are kept with ``status = 'deleted'`` so removals stay auditable,
        and their dead-letter rows are cleared.

        Args:
            page_ids: Pages to delete.

        Returns:
            The number of pages soft-deleted and of chunks removed.
        """
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
        """Dead-letter a page, or count another attempt if it is already there.

        Args:
            page_id: Page that failed.
            stage: Stage that failed it.
            error: The exception; its type and message are stored, up to 4000 characters.
            run_id: Airflow run ID.
        """
        self._execute(
            "record_failure",
            page_id=page_id,
            stage=stage,
            error=f"{type(error).__name__}: {error}"[:4000],
            run_id=run_id,
        )

    def clear_failures(self, page_ids: Iterable[str]) -> None:
        """Remove pages from the dead-letter table.

        Args:
            page_ids: Pages to remove.
        """
        ids = list(page_ids)
        if ids:
            self._execute("clear_failures", page_ids=ids)

    def retryable_failures(self, max_attempts: int) -> list[str]:
        """Return dead-lettered pages that have retries left.

        Args:
            max_attempts: Attempts after which a page is parked.

        Returns:
            Page IDs with fewer than ``max_attempts`` attempts, sorted.
        """
        return [r["page_id"] for r in self._all("retryable_failures", max_attempts=max_attempts)]

    def count_parked_failures(self, max_attempts: int) -> int:
        """Count pages that used up their retries and need a human.

        Args:
            max_attempts: Attempts after which a page is parked.

        Returns:
            The number of parked pages.
        """
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
        """Insert or update the audit row for a run.

        Args:
            pipeline: Pipeline name.
            run_id: Airflow run ID.
            status: Overall run status.
            stats: Run statistics, stored as JSON.
            failed_stages: Names of the stages that failed.
        """
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
        """Run a named query that returns no rows.

        Args:
            name: Query file name in ``sql/queries`` without ``.sql``.
            **params: Query parameters.
        """
        with self._conn.cursor() as cur:
            cur.execute(query(name), params)

    def _one(self, name: str, **params: Any) -> dict[str, Any] | None:
        """Run a named query and return its first row.

        Args:
            name: Query file name in ``sql/queries`` without ``.sql``.
            **params: Query parameters.

        Returns:
            The first row, or None if there are none.
        """
        with self._conn.cursor() as cur:
            cur.execute(query(name), params)
            row: dict[str, Any] | None = cur.fetchone()
            return row

    def _all(self, name: str, **params: Any) -> list[dict[str, Any]]:
        """Run a named query and return all its rows.

        Args:
            name: Query file name in ``sql/queries`` without ``.sql``.
            **params: Query parameters.

        Returns:
            The rows.
        """
        with self._conn.cursor() as cur:
            cur.execute(query(name), params)
            rows: list[dict[str, Any]] = cur.fetchall()
            return rows


def chunk_metadata(document: PageDocument, chunk_index: int) -> dict[str, Any]:
    """Build the filterable source metadata stored with each chunk.

    Volatile fields (version, last_modified, chunk_count) live on the pages
    table only, so a save that changes nothing indexable, or a chunk added at
    the end of a page, does not rewrite every chunk row.

    Args:
        document: Page the chunk belongs to.
        chunk_index: Position of the chunk within the page.

    Returns:
        Page and section fields for the chunk's ``metadata`` column.
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


def apply_schema_management(
    database_connection_string: str, embedding_dimensions: int
) -> list[str]:
    """Create any missing schema objects.

    Every script runs on every call, so each must be rerunnable (IF NOT EXISTS,
    guarded changes). ``:embedding_dimensions`` is replaced with the configured
    vector size, the same variable ``psql -v embedding_dimensions=N`` would set.
    A database lock stops concurrent runs applying scripts at the same time.

    Args:
        database_connection_string: libpq connection URI.
        embedding_dimensions: Vector size for the ``chunks.embedding`` column.

    Returns:
        The names of the scripts run, in order.
    """
    applied: list[str] = []
    with psycopg.connect(database_connection_string, autocommit=True) as conn:
        conn.execute(query("schema_management_lock"))
        try:
            for script in schema_management():
                log.info("Applying schema script %s", script.name)
                ddl = _DIMENSIONS_VAR.sub(str(int(embedding_dimensions)), script.read_text())
                with conn.transaction():
                    conn.execute(ddl.encode())
                applied.append(script.name)
        finally:
            conn.execute(query("schema_management_unlock"))
    return applied
