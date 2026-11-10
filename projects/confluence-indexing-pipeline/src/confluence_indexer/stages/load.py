"""Load: embed only new or changed chunks and write pages atomically to pgvector."""

from __future__ import annotations

import logging
import time
from collections.abc import Iterable, Iterator, Sequence
from typing import Any, TypeVar

from ..config import PipelineConfig
from ..integrations.embeddings import EmbeddingProvider
from ..integrations.landing_zone import LandingZone
from ..integrations.vector_store import PgVectorStore
from ..models import PageDocument
from .base import StageReport, enforce_failure_budget, page_failed

log = logging.getLogger(__name__)

T = TypeVar("T")


def load(
    config: PipelineConfig,
    *,
    landing: LandingZone,
    store: PgVectorStore,
    embedder: EmbeddingProvider,
    run_id: str,
    documents_uri: str,
) -> StageReport:
    """Embed new or changed chunks and write pages atomically to pgvector."""
    started = time.monotonic()
    report = StageReport("load")
    store.check_schema(config.embedding.dimensions)
    for group in _batched(landing.iter_jsonl(documents_uri), config.guardrails.load_batch_pages):
        _load_group(
            config, [PageDocument.from_dict(d) for d in group], store, embedder, report, run_id
        )
    enforce_failure_budget(config, report, attempted=report.counts["pages_total"])
    report.seconds = time.monotonic() - started
    return report


def _load_group(
    config: PipelineConfig,
    documents: Sequence[PageDocument],
    store: PgVectorStore,
    embedder: EmbeddingProvider,
    report: StageReport,
    run_id: str,
) -> None:
    embedding_version = config.embedding.embedding_version
    indexed = store.get_indexed_pages([d.page_id for d in documents])
    pending: list[PageDocument] = []
    for document in documents:
        report.counts["pages_total"] += 1
        current = indexed.get(document.page_id)
        if (
            current is not None
            and current.content_hash == document.content_hash
            and current.embedding_version == embedding_version
        ):
            # New Confluence version, but nothing that reaches the index changed.
            try:
                store.touch_page(document)
                store.clear_failures([document.page_id])
                report.counts["pages_content_unchanged"] += 1
            except Exception as exc:
                page_failed(store, report, document.page_id, exc, run_id)
        else:
            pending.append(document)
    if not pending:
        return

    vectors, failed = _resolve_vectors(pending, store, embedder, embedding_version, report, run_id)
    for document in pending:
        if document.page_id in failed:
            continue
        try:
            removed = store.upsert_page(document, vectors, embedding_version)
            store.clear_failures([document.page_id])
        except Exception as exc:
            page_failed(store, report, document.page_id, exc, run_id)
            continue
        report.counts["pages_indexed"] += 1
        report.counts["chunks_written"] += len(document.chunks)
        report.counts["chunks_deleted"] += removed


def _resolve_vectors(
    documents: Sequence[PageDocument],
    store: PgVectorStore,
    embedder: EmbeddingProvider,
    embedding_version: str,
    report: StageReport,
    run_id: str,
) -> tuple[dict[str, Any], set[str]]:
    """Vectors for every chunk hash: reused from the store where possible, else embedded.

    Returns the vectors and the IDs of pages that could not be embedded.
    """
    chunks = [chunk for document in documents for chunk in document.chunks]
    vectors: dict[str, Any] = dict(
        store.find_embeddings((c.content_hash for c in chunks), embedding_version)
    )
    report.counts["chunks_reused"] += sum(1 for c in chunks if c.content_hash in vectors)

    def missing_for(docs: Iterable[PageDocument]) -> dict[str, tuple[str, int]]:
        missing: dict[str, tuple[str, int]] = {}
        for document in docs:
            for chunk in document.chunks:
                if chunk.content_hash not in vectors:
                    missing.setdefault(
                        chunk.content_hash, (chunk.embedding_text, chunk.token_count)
                    )
        return missing

    def embed(missing: dict[str, tuple[str, int]]) -> None:
        if not missing:
            return
        new = embedder.embed([text for text, _ in missing.values()])
        vectors.update(zip(missing, new, strict=True))
        report.counts["chunks_embedded"] += len(missing)
        report.counts["embedding_tokens"] += sum(tokens for _, tokens in missing.values())

    failed: set[str] = set()
    try:
        embed(missing_for(documents))
    except Exception:
        # One bad input (or a transient fault that outlived SDK retries) should
        # not sink the whole batch: retry page by page and dead-letter the rest.
        log.warning("Batch embedding failed; retrying %d pages individually", len(documents))
        for document in documents:
            try:
                embed(missing_for([document]))
            except Exception as exc:
                failed.add(document.page_id)
                page_failed(store, report, document.page_id, exc, run_id)
    return vectors, failed


def _batched(items: Iterable[T], size: int) -> Iterator[list[T]]:
    batch: list[T] = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch
