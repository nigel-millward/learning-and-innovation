"""Run summary: CloudWatch metrics, run audit row and degraded-success alerts."""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..config import PipelineConfig
from ..integrations.observability import Alerter, MetricsPublisher
from ..integrations.vector_store import PgVectorStore
from .base import STAGES, StageReport

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class RunSummary:
    status: str
    failed_stages: tuple[str, ...]
    counts: dict[str, float]
    seconds: dict[str, float]

    @property
    def succeeded(self) -> bool:
        return self.status == "success"


def summarise(
    config: PipelineConfig,
    reports: Mapping[str, Mapping[str, Any] | None],
    *,
    run_id: str,
    store: PgVectorStore | None,
    metrics: MetricsPublisher,
    alerter: Alerter,
) -> RunSummary:
    """Publish run metrics and status; alert on degraded success.

    Hard failures are alerted by the failing task itself, which has the
    exception to hand, so this only alerts on runs that succeeded with problems.
    """
    parsed = {name: StageReport.from_dict(r) for name, r in reports.items() if r}
    failed_stages = tuple(stage for stage in STAGES if stage not in parsed)
    status = "failed" if failed_stages else "success"

    counts: dict[str, float] = {
        f"{_camel(name)}{_camel(key)}": value
        for name, report in parsed.items()
        for key, value in report.counts.items()
    }
    counts["RunSucceeded"] = int(status == "success")
    counts["RunFailed"] = int(status == "failed")
    seconds = {f"{_camel(name)}Duration": report.seconds for name, report in parsed.items()}
    seconds["RunDuration"] = sum(report.seconds for report in parsed.values())

    parked = 0
    if store is not None:
        try:
            parked = store.count_parked_failures(config.guardrails.max_page_attempts)
            counts["DeadLetterParkedPages"] = parked
            store.record_run(config.pipeline_name, run_id, status, counts, failed_stages)
        except Exception:
            log.exception("Could not record run in the database")

    metrics.publish(counts, seconds)

    page_failures = sum(r.counts.get("pages_failed", 0) for r in parsed.values())
    details = {"run_id": run_id, "counts": counts, "seconds": seconds}
    if status == "success" and (page_failures or parked):
        alerter.send(
            "WARNING",
            f"Completed with {page_failures} failed pages, {parked} parked",
            {**details, "action": "Inspect confluence_index.failed_pages for errors"},
        )
    elif status == "success" and config.observability.notify_on_success:
        alerter.send("INFO", "Run succeeded", details)

    return RunSummary(status, failed_stages, counts, seconds)


def _camel(name: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[_\W]+", name) if part)
