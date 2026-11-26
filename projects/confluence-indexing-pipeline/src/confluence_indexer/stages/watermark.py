"""Commit load_date: advance the incremental-extraction load timestamp."""

from __future__ import annotations

import logging
from datetime import datetime

from ..config import PipelineConfig
from ..integrations.vector_store import PgVectorStore
from .base import StageReport

log = logging.getLogger(__name__)


def commit_watermark(
    config: PipelineConfig, *, store: PgVectorStore, run_id: str, run_started_at: datetime
) -> StageReport:
    """Advance the load_date to this run's start time, never moving it backwards.

    Only reached when extract, transform and load succeeded, so pages that
    changed during a failed run are picked up again next time. The store keeps
    the later of the current and new values, so a late or stale run cannot
    rewind it.

    Args:
        config: Pipeline configuration supplying the pipeline name.
        store: Vector store that holds the load date.
        run_id: ID of the pipeline run, recorded with the load date.
        run_started_at: Start time captured by the extract stage.

    Returns:
        The stage report; ``outputs`` holds the stored ``load_date``, which is
        the existing value if that was already later than ``run_started_at``.
    """
    report = StageReport("commit_watermark")
    stored = store.advance_load_date(config.pipeline_name, run_started_at, run_id)
    report.outputs = {"load_date": stored.isoformat()}
    log.info("Load date is now %s", stored.isoformat())
    return report
