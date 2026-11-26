"""Shared stage plumbing: reports, errors and the per-page failure policy.

Every stage takes its collaborators explicitly and returns a ``StageReport``,
so stages run the same under Airflow and in tests (with fakes). Stages
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
    """Anything that can dead-letter a failed page (in practice ``PgVectorStore``)."""

    def record_failure(self, page_id: str, stage: str, error: BaseException, run_id: str) -> None:
        """Record that a page failed in a stage, so it is retried on a later run.

        Args:
            page_id: Confluence ID of the failed page.
            stage: Name of the stage the page failed in.
            error: The exception that caused the failure.
            run_id: ID of the pipeline run.
        """
        ...


class StageFailedError(RuntimeError):
    """Too many pages failed for the stage to be trusted; Airflow should retry it."""


class DeletionGuardError(RuntimeError):
    """Reconciliation would delete an implausibly large share of the index."""


@dataclass
class StageReport:
    """Outcome of one stage run, passed between Airflow tasks via XCom as a dict.

    Attributes:
        stage: Name of the stage.
        counts: Named counters (pages extracted, chunks embedded, failures, ...).
        seconds: Wall-clock duration of the stage.
        outputs: Values later stages need, such as S3 URIs and the run start time.
    """

    stage: str
    counts: Counter[str] = field(default_factory=Counter)
    seconds: float = 0.0
    outputs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialise the report to plain JSON-compatible types.

        Returns:
            The report as a dict, with ``seconds`` rounded to milliseconds.
        """
        return {
            "stage": self.stage,
            "counts": dict(self.counts),
            "seconds": round(self.seconds, 3),
            "outputs": self.outputs,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> StageReport:
        """Rebuild a report from the output of ``to_dict``.

        Args:
            data: A serialised report; only ``stage`` is required.

        Returns:
            The reconstructed report.
        """
        return cls(
            stage=data["stage"],
            counts=Counter(data.get("counts", {})),
            seconds=float(data.get("seconds", 0.0)),
            outputs=dict(data.get("outputs", {})),
        )


def page_failed(
    store: FailureRecorder, report: StageReport, page_id: str, exc: Exception, run_id: str
) -> None:
    """Dead-letter one page so the stage can carry on; it is retried next run.

    Logs the error and counts it in ``pages_failed``. A failure to record the
    dead letter is logged rather than raised.

    Args:
        store: Where the failure is recorded.
        report: The current stage's report.
        page_id: Confluence ID of the failed page.
        exc: The exception that caused the failure.
        run_id: ID of the pipeline run.
    """
    log.error("Page %s failed in %s: %s", page_id, report.stage, exc, exc_info=exc)
    report.counts["pages_failed"] += 1
    try:
        store.record_failure(page_id, report.stage, exc, run_id)
    except Exception:
        log.exception("Could not dead-letter page %s", page_id)


def enforce_failure_budget(config: PipelineConfig, report: StageReport, attempted: int) -> None:
    """Fail the stage (so Airflow retries it) when too many pages failed to trust it.

    Args:
        config: Pipeline config supplying ``guardrails.max_failure_ratio``.
        report: The stage's report, whose ``pages_failed`` count is checked.
        attempted: Number of pages the stage attempted; zero never fails.

    Raises:
        StageFailedError: If the share of failed pages exceeds the maximum ratio.
    """
    failed = report.counts["pages_failed"]
    if attempted and failed / attempted > config.guardrails.max_failure_ratio:
        raise StageFailedError(
            f"{report.stage}: {failed} of {attempted} pages failed "
            f"(> {config.guardrails.max_failure_ratio:.0%}); see confluence_index.failed_pages"
        )
