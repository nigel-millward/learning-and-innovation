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
    """Find pages changed since the load_date and land their raw payloads in S3.

    The CQL search starts ``load_date_overlap`` before the stored load date (or
    covers everything on a full refresh or first run). A changed page is fetched
    only if it is unindexed, newer than the indexed version, or was embedded
    under a different embedding version; previously failed pages still within
    their attempt budget are retried too. A manifest of the landed pages is
    written for the transform stage.

    Args:
        config: Pipeline configuration.
        confluence: Client used to search for and fetch pages.
        landing: S3 landing zone for raw payloads and the manifest.
        store: Vector store holding the load date, indexed pages and dead letters.
        run_id: ID of the pipeline run, used to namespace landed objects.
        full_refresh: Ignore the load date and refetch every page.
        now: Run start time; defaults to the current UTC time.

    Returns:
        The stage report; ``outputs`` holds ``manifest_uri`` and ``run_started_at``.

    Raises:
        StageFailedError: If too many pages failed to be fetched or landed.
    """
    started = time.monotonic()
    report = StageReport("extract")
    # Captured before searching: anything modified from here on is picked up next run.
    run_started_at = now or datetime.now(UTC)
    embedding_version = config.embedding.embedding_version

    load_date = None if full_refresh else store.get_load_date(config.pipeline_name)
    since = load_date - config.guardrails.load_date_overlap if load_date else None
    log.info("Extracting pages modified since %s (full_refresh=%s)", since, full_refresh)

    changed_pages = {page.page_id: page.version for page in confluence.changed_pages(since)}
    indexed = store.get_indexed_pages(list(changed_pages))
    page_ids_to_fetch = [
        page_id
        for page_id, version in sorted(changed_pages.items())
        if full_refresh or _needs_fetch(indexed.get(page_id), version, embedding_version)
    ]
    fetching = set(page_ids_to_fetch)
    retries = [
        page_id
        for page_id in store.retryable_failures(config.guardrails.max_page_attempts)
        if page_id not in fetching
    ]
    report.counts.update(
        pages_changed=len(changed_pages),
        pages_already_indexed=len(changed_pages) - len(page_ids_to_fetch),
        pages_retried=len(retries),
    )

    pages: list[dict[str, Any]] = []
    for page_id in [*page_ids_to_fetch, *retries]:
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
    enforce_failure_budget(config, report, attempted=len(page_ids_to_fetch) + len(retries))
    report.seconds = time.monotonic() - started
    return report


def _needs_fetch(indexed: IndexedPage | None, version: int, embedding_version: str) -> bool:
    """Decide whether a changed page must be re-extracted.

    Args:
        indexed: The page's current index entry, or None if it is not indexed.
        version: The page's current Confluence version.
        embedding_version: The configured embedding version.

    Returns:
        True if the page is unindexed, has a newer version, or was embedded
        under a different embedding version.
    """
    return (
        indexed is None
        or indexed.version < version
        or indexed.embedding_version != embedding_version
    )
