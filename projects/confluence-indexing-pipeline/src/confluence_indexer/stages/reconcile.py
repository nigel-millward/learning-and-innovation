"""Reconcile: remove vectors for pages deleted or hidden in Confluence."""

from __future__ import annotations

import logging
import time
from datetime import datetime

from ..config import PipelineConfig
from ..integrations.confluence import ConfluenceClient
from ..integrations.vector_store import PgVectorStore
from .base import DeletionGuardError, StageReport

log = logging.getLogger(__name__)


def reconcile(
    config: PipelineConfig,
    *,
    confluence: ConfluenceClient,
    store: PgVectorStore,
    run_started_at: datetime,
    allow_mass_delete: bool = False,
) -> StageReport:
    """Delete vectors for pages that no longer exist (or are no longer visible).

    CQL cannot report deletions, so the full set of live page IDs is compared
    with the index. Pages indexed during this run are excluded, which avoids
    racing the search index for pages created moments ago.
    """
    started = time.monotonic()
    report = StageReport("reconcile")
    live = confluence.list_page_ids()
    indexed = store.list_active_page_ids(indexed_before=run_started_at)
    removed = indexed - live
    total = store.count_active_pages()
    report.counts.update(pages_live=len(live), pages_missing=len(removed))

    guard = config.guardrails
    ratio = len(removed) / total if total else 0.0
    if len(removed) > guard.mass_delete_min_pages and ratio > guard.max_delete_ratio:
        if not allow_mass_delete:
            raise DeletionGuardError(
                f"Refusing to delete {len(removed)} of {total} indexed pages ({ratio:.0%} > "
                f"{guard.max_delete_ratio:.0%}). Check the service account's space permissions; "
                "if the deletions are genuine, re-run with allow_mass_delete=true."
            )
        log.warning("Mass delete of %d pages allowed by override", len(removed))

    pages, chunks = store.mark_pages_deleted(sorted(removed))
    report.counts.update(pages_deleted=pages, chunks_deleted=chunks)
    if removed:
        log.info("Removed %d pages (%d chunks) no longer in Confluence", pages, chunks)
    report.seconds = time.monotonic() - started
    return report
