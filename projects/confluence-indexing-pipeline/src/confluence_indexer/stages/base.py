"""Shared stage plumbing: reports, errors and the per-page failure policy.

Every stage takes its collaborators explicitly and returns a ``StageReport``,
so stages run the same under Airflow, the CLI and tests (with fakes). Stages
are idempotent: re-running one (an Airflow retry, a manual clear, a replay)
converges on the same index state without duplicate rows and without paying
to re-embed text that already has a vector.
"""

from __future__ import annotations

import logging
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from ..config import PipelineConfig

log = logging.getLogger(__name__)

# Every stage a successful run must complete, in DAG order.
STAGES = ("extract", "transform", "load", "commit_watermark", "reconcile")


class FailureRecorder(Protocol):
    def record_failure(
        self, page_id: str, stage: str, error: BaseException, run_id: str
    ) -> None: ...


class StageFailedError(RuntimeError):
    """Too many pages failed for the stage to be trusted; Airflow should retry it."""


class DeletionGuardError(RuntimeError):
    """Reconciliation would delete an implausibly large share of the index."""


@dataclass
class StageReport:
    stage: str
    counts: Counter[str] = field(default_factory=Counter)
    seconds: float = 0.0
    outputs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "counts": dict(self.counts),
            "seconds": round(self.seconds, 3),
            "outputs": self.outputs,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> StageReport:
        return cls(
            stage=data["stage"],
            counts=Counter(data.get("counts", {})),
            seconds=float(data.get("seconds", 0.0)),
            outputs=dict(data.get("outputs", {})),
        )


def page_failed(
    store: FailureRecorder, report: StageReport, page_id: str, exc: Exception, run_id: str
) -> None:
    """Dead-letter one page so the stage can carry on; it is retried next run."""
    log.error("Page %s failed in %s: %s", page_id, report.stage, exc, exc_info=exc)
    report.counts["pages_failed"] += 1
    try:
        store.record_failure(page_id, report.stage, exc, run_id)
    except Exception:
        log.exception("Could not dead-letter page %s", page_id)


def enforce_failure_budget(config: PipelineConfig, report: StageReport, attempted: int) -> None:
    """Fail the stage (so Airflow retries it) when too many pages failed to trust it."""
    failed = report.counts["pages_failed"]
    if attempted and failed / attempted > config.guardrails.max_failure_ratio:
        raise StageFailedError(
            f"{report.stage}: {failed} of {attempted} pages failed "
            f"(> {config.guardrails.max_failure_ratio:.0%}); see confluence_index.failed_pages"
        )
