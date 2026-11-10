"""Extract: incremental CQL search, then land raw page payloads in S3."""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from typing import Any

from ..config import PipelineConfig
from ..integrations.confluence import ConfluenceClient
from ..integrations.landing_zone import LandingZone
from ..integrations.vector_store import PgVectorStore
from ..models import IndexedPage
from .base import StageReport, enforce_failure_budget, page_failed

log = logging.getLogger(__name__)


def extract(
    config: PipelineConfig,
    *,
    confluence: ConfluenceClient,
    landing: LandingZone,
    store: PgVectorStore,
    run_id: str,
    full_refresh: bool = False,
    now: datetime | None = None,
) -> StageReport:
    """Find pages changed since the watermark and land their raw payloads in S3."""
    started = time.monotonic()
    report = StageReport("extract")
    # Captured before searching: anything modified from here on is picked up next run.
    run_started_at = now or datetime.now(UTC)
    embedding_version = config.embedding.embedding_version

    watermark = None if full_refresh else store.get_watermark(config.pipeline_name)
    since = watermark - config.guardrails.watermark_overlap if watermark else None
    log.info("Extracting pages modified since %s (full_refresh=%s)", since, full_refresh)

    hits = {hit.page_id: hit.version for hit in confluence.changed_pages(since)}
    indexed = store.get_indexed_pages(list(hits))
    to_fetch = [
        page_id
        for page_id, version in sorted(hits.items())
        if full_refresh or _needs_fetch(indexed.get(page_id), version, embedding_version)
    ]
    fetching = set(to_fetch)
    retries = [
        page_id
        for page_id in store.retryable_failures(config.guardrails.max_page_attempts)
        if page_id not in fetching
    ]
    report.counts.update(
        pages_changed=len(hits),
        pages_already_indexed=len(hits) - len(to_fetch),
        pages_retried=len(retries),
    )

    pages: list[dict[str, Any]] = []
    for page_id in [*to_fetch, *retries]:
        try:
            payload = confluence.get_page(page_id)
            if payload is None:
                # Deleted or restricted since the search ran; reconcile removes it.
                report.counts["pages_vanished"] += 1
                store.clear_failures([page_id])
                continue
            raw_uri = landing.put_raw_page(payload, run_id)
            pages.append(
                {"page_id": page_id, "version": payload["version"]["number"], "raw_uri": raw_uri}
            )
            report.counts["pages_extracted"] += 1
        except Exception as exc:
            page_failed(store, report, page_id, exc, run_id)

    manifest_uri = landing.put_run_json(
        run_id,
        "extract_manifest.json",
        {
            "run_id": run_id,
            "run_started_at": run_started_at.isoformat(),
            "since": since.isoformat() if since else None,
            "full_refresh": full_refresh,
            "embedding_version": embedding_version,
            "pages": pages,
        },
    )
    report.outputs = {"manifest_uri": manifest_uri, "run_started_at": run_started_at.isoformat()}
    enforce_failure_budget(config, report, attempted=len(to_fetch) + len(retries))
    report.seconds = time.monotonic() - started
    return report


def _needs_fetch(indexed: IndexedPage | None, version: int, embedding_version: str) -> bool:
    return (
        indexed is None
        or indexed.version < version
        or indexed.embedding_version != embedding_version
    )
