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
    """Advance the load_date. Only reached when extract, transform and load succeeded."""
    report = StageReport("commit_watermark")
    stored = store.advance_load_date(config.pipeline_name, run_started_at, run_id)
    report.outputs = {"load_date": stored.isoformat()}
    log.info("Load date is now %s", stored.isoformat())
    return report
