r"""Confluence -> pgvector indexing DAG for Airflow 3.

Daily incremental indexing of Confluence pages into PostgreSQL/pgvector.

```
schema_management -> extract -> transform -> load -> commit_watermark --> publish_run_status
                                                  \-> reconcile -------/
```

* **schema_management** - creates any missing schema objects (schema, tables,
  indexes). Every statement is rerunnable, so existing objects and data are kept.
* **extract** - CQL search for pages modified since the load_date (minus an
  overlap), plus dead-lettered pages due a retry; lands raw payloads in S3.
* **transform** - cleans storage-format XHTML and chunks it; stages JSONL in S3.
* **load** - reuses vectors for unchanged chunk hashes, embeds the rest, and
  replaces each page's rows atomically. Updates the `confluence_index` asset.
* **commit_watermark** - advances the load_date only after a successful load.
* **reconcile** - removes vectors for pages deleted or hidden in Confluence,
  behind a mass-deletion guard. Updates the `confluence_index` asset.
* **publish_run_status** - always runs; CloudWatch metrics, run audit row,
  SNS warning on degraded success. Fails the DAG run if any stage failed.

Params: `full_refresh` re-reads every page (embeddings are still reused by
content hash, so this is cheap unless the text changed); `allow_mass_delete`
overrides the deletion guard after a confirmed bulk removal.

To re-process a past run without calling Confluence, clear `transform` and `load`
on that run (without downstream tasks); they re-read the run's extract manifest
from XCom.

Credentials come from Airflow Connections when defined (`confluence_default`,
`pgvector_default`, `openai_default`), otherwise from environment variables.
Everything else is configured by environment variables; see `.env.example`.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pendulum
from airflow.sdk import Asset, Param, dag, task

from confluence_indexer.orchestration.airflow_runtime import (
    alert_task_failure,
    bool_param,
    pipeline_config,
    pull_output,
    pull_reports,
    push_report,
    run_id,
)

# XCom keys: names in a stage report's "outputs" that downstream stages need.
# push_report also pushes each full report, under airflow_runtime.REPORT_KEY.
MANIFEST_URI_KEY = "manifest_uri"
DOCUMENTS_URI_KEY = "documents_uri"
RUN_STARTED_AT_KEY = "run_started_at"

# Downstream DAGs (evaluation, cache warm-up, ...) can schedule on index updates.
CONFLUENCE_INDEX = Asset("confluence_index")

PIPELINE_TASKS = ("extract", "transform", "load", "commit_watermark", "reconcile")


@dag(
    dag_id="confluence_indexing",
    schedule="0 2 * * *",
    start_date=pendulum.datetime(2026, 11, 1, tz="Europe/London"),
    catchup=False,
    # The load_date is a single row; concurrent runs would race to move it.
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=8),
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "execution_timeout": timedelta(hours=2),
        "on_failure_callback": alert_task_failure,
    },
    params={
        "full_refresh": Param(False, type="boolean", description="Ignore the load_date"),
        "allow_mass_delete": Param(False, type="boolean", description="Bypass deletion guard"),
    },
    tags=["confluence", "rag", "pgvector", "indexing"],
    doc_md=__doc__,
)
def confluence_indexing() -> None:
    """Define the confluence_indexing DAG's tasks and their dependencies.

    The task order is described in the module docstring, which is also the
    DAG's documentation in the Airflow UI.
    """

    @task
    def schema_management() -> None:
        """Create any missing schema objects in the vector store."""
        from confluence_indexer.orchestration.tasks import run_schema_management

        run_schema_management(pipeline_config())

    @task
    def extract() -> None:
        """Land changed and retry-due pages in S3 and push the manifest URI and start time."""
        from confluence_indexer.orchestration.tasks import run_extract

        report = run_extract(pipeline_config(), run_id(), full_refresh=bool_param("full_refresh"))
        push_report(report, MANIFEST_URI_KEY, RUN_STARTED_AT_KEY)

    @task
    def transform() -> None:
        """Clean and chunk the extracted pages and push the staged documents URI."""
        from confluence_indexer.orchestration.tasks import run_transform

        manifest_uri = pull_output("extract", MANIFEST_URI_KEY)
        report = run_transform(pipeline_config(), run_id(), manifest_uri)
        push_report(report, DOCUMENTS_URI_KEY)

    @task(execution_timeout=timedelta(hours=4), outlets=[CONFLUENCE_INDEX])
    def load() -> None:
        """Embed the staged documents and write them to the vector store."""
        from confluence_indexer.orchestration.tasks import run_load

        documents_uri = pull_output("transform", DOCUMENTS_URI_KEY)
        push_report(run_load(pipeline_config(), run_id(), documents_uri))

    @task
    def commit_watermark() -> None:
        """Advance the load_date to the start time of this run's extract."""
        from confluence_indexer.orchestration.tasks import run_commit_watermark

        started_at = pull_output("extract", RUN_STARTED_AT_KEY)
        push_report(run_commit_watermark(pipeline_config(), run_id(), started_at))

    @task(outlets=[CONFLUENCE_INDEX])
    def reconcile() -> None:
        """Remove pages deleted or hidden in Confluence, behind the mass-deletion guard."""
        from confluence_indexer.orchestration.tasks import run_reconcile

        started_at = pull_output("extract", RUN_STARTED_AT_KEY)
        report = run_reconcile(
            pipeline_config(),
            run_id(),
            started_at,
            allow_mass_delete=bool_param("allow_mass_delete"),
        )
        push_report(report)

    @task(trigger_rule="all_done", retries=0, on_failure_callback=None)
    def publish_run_status() -> dict[str, Any]:
        """Publish metrics, the audit row and alerts for the run, then fail if a stage failed.

        Returns:
            The run's overall status and its aggregated counts.

        Raises:
            RuntimeError: If any pipeline stage failed or did not run.
        """
        from confluence_indexer.orchestration.tasks import run_summary

        # A failed or skipped task pushes no report, so a missing report = failed stage.
        summary = run_summary(pipeline_config(), run_id(), pull_reports(PIPELINE_TASKS))
        if not summary.succeeded:
            # This is the DAG's only leaf, so it must fail for the run to show as failed.
            raise RuntimeError(f"Pipeline stages failed: {', '.join(summary.failed_stages)}")
        return {"status": summary.status, "counts": summary.counts}

    # Tasks share data through XCom keys, not arguments, so dependencies are explicit.
    # commit_watermark and reconcile take load as upstream so they wait for a successful load.
    extracted, transformed, loaded = extract(), transform(), load()
    finished = [commit_watermark(), reconcile()]
    schema_management() >> extracted >> transformed >> loaded >> finished
    extracted >> finished
    finished >> publish_run_status()


confluence_indexing()
