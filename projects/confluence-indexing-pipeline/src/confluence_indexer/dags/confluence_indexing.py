"""
### Confluence -> pgvector indexing (Airflow 3)

Daily incremental indexing of Confluence pages into PostgreSQL/pgvector.

```
extract -> transform -> load -> commit_watermark --> publish_run_status
                             \\-> reconcile -------/
```

* **extract** - CQL search for pages modified since the watermark (minus an
  overlap), plus dead-lettered pages due a retry; lands raw payloads in S3.
* **transform** - cleans storage-format XHTML and chunks it; stages JSONL in S3.
* **load** - reuses vectors for unchanged chunk hashes, embeds the rest, and
  replaces each page's rows atomically. Updates the `confluence_index` asset.
* **commit_watermark** - advances the watermark only after a successful load.
* **reconcile** - removes vectors for pages deleted or hidden in Confluence,
  behind a mass-deletion guard. Updates the `confluence_index` asset.
* **publish_run_status** - always runs; CloudWatch metrics, run audit row,
  SNS warning on degraded success. Fails the DAG run if any stage failed.

Params: `full_refresh` re-reads every page (embeddings are still reused by
content hash, so this is cheap unless the text changed); `allow_mass_delete`
overrides the deletion guard after a confirmed bulk removal.

Credentials come from Airflow Connections when defined (`confluence_default`,
`pgvector_default`, `openai_default`), otherwise from environment variables.
Everything else is configured by environment variables; see `.env.example`.
"""

from __future__ import annotations

import logging
import os
from datetime import timedelta
from typing import Any

import pendulum
from airflow.sdk import Asset, Connection, Param, dag, get_current_context, task
from airflow.sdk.exceptions import AirflowNotFoundException

log = logging.getLogger(__name__)

# Downstream DAGs (evaluation, cache warm-up, ...) can schedule on index updates.
CONFLUENCE_INDEX = Asset("confluence_index")

PIPELINE_TASKS = ("extract", "transform", "load", "commit_watermark", "reconcile")

# Airflow Connection field -> pipeline environment variable.
CONNECTION_ENV: dict[str, dict[str, str]] = {
    "confluence_default": {
        "host": "CONFLUENCE_BASE_URL",
        "login": "CONFLUENCE_USERNAME",
        "password": "CONFLUENCE_API_TOKEN",
    },
    "pgvector_default": {"uri": "PG_DSN"},
    "openai_default": {"password": "OPENAI_API_KEY"},
}


def _config() -> Any:
    """Build pipeline config from the environment, overlaid with Airflow Connections.

    Imported lazily: the DAG processor parses this file often and must not pay
    for (or fail on) the pipeline's dependencies at parse time.
    """
    from confluence_indexer.config import PipelineConfig

    env = dict(os.environ)
    for conn_id, fields in CONNECTION_ENV.items():
        try:
            conn = Connection.get(conn_id)
        except AirflowNotFoundException:
            continue
        for field, variable in fields.items():
            value = conn.get_uri() if field == "uri" else getattr(conn, field, None)
            if field == "host" and value and not value.startswith(("http://", "https://")):
                value = f"https://{value}"
            if value:
                env[variable] = value
    return PipelineConfig.from_env(env)


def _run_id() -> str:
    return str(get_current_context()["run_id"])


def _param(name: str) -> bool:
    return bool(get_current_context()["params"][name])


def _alert_task_failure(context: dict[str, Any]) -> None:
    """Send an SNS alert when a task fails after exhausting its retries."""
    try:
        from confluence_indexer.tasks import alerter

        ti = context["task_instance"]
        alerter(_config()).send(
            "CRITICAL",
            f"Task {ti.task_id} failed",
            {
                "dag_id": ti.dag_id,
                "task_id": ti.task_id,
                "run_id": context.get("run_id"),
                "try_number": ti.try_number,
                "error": repr(context.get("exception")),
                "log_url": getattr(ti, "log_url", None),
            },
        )
    except Exception:
        log.exception("Failure callback could not send alert")


@dag(
    dag_id="confluence_indexing",
    schedule="0 2 * * *",
    start_date=pendulum.datetime(2026, 11, 1, tz="Europe/London"),
    catchup=False,
    # The watermark is a single row; concurrent runs would race to move it.
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=8),
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "execution_timeout": timedelta(hours=2),
        "on_failure_callback": _alert_task_failure,
    },
    params={
        "full_refresh": Param(False, type="boolean", description="Ignore the watermark"),
        "allow_mass_delete": Param(False, type="boolean", description="Bypass deletion guard"),
    },
    tags=["confluence", "rag", "pgvector", "indexing"],
    doc_md=__doc__,
)
def confluence_indexing() -> None:
    @task
    def extract() -> dict[str, Any]:
        from confluence_indexer.tasks import run_extract

        return run_extract(_config(), _run_id(), full_refresh=_param("full_refresh"))

    @task
    def transform(extract_report: dict[str, Any]) -> dict[str, Any]:
        from confluence_indexer.tasks import run_transform

        return run_transform(_config(), _run_id(), extract_report["outputs"]["manifest_uri"])

    @task(execution_timeout=timedelta(hours=4), outlets=[CONFLUENCE_INDEX])
    def load(transform_report: dict[str, Any]) -> dict[str, Any]:
        from confluence_indexer.tasks import run_load

        return run_load(_config(), _run_id(), transform_report["outputs"]["documents_uri"])

    @task
    def commit_watermark(
        extract_report: dict[str, Any], load_report: dict[str, Any]
    ) -> dict[str, Any]:
        from confluence_indexer.tasks import run_commit_watermark

        # load_report is unused: taking it makes the watermark wait for a successful load.
        started_at = extract_report["outputs"]["run_started_at"]
        return run_commit_watermark(_config(), _run_id(), started_at)

    @task(outlets=[CONFLUENCE_INDEX])
    def reconcile(extract_report: dict[str, Any], load_report: dict[str, Any]) -> dict[str, Any]:
        from confluence_indexer.tasks import run_reconcile

        return run_reconcile(
            _config(),
            _run_id(),
            extract_report["outputs"]["run_started_at"],
            allow_mass_delete=_param("allow_mass_delete"),
        )

    @task(trigger_rule="all_done", retries=0, on_failure_callback=None)
    def publish_run_status() -> dict[str, Any]:
        from confluence_indexer.tasks import run_summary

        ti = get_current_context()["ti"]
        # A failed or skipped task pushes no XCom, so a missing report = failed stage.
        reports = {name: ti.xcom_pull(task_ids=name) for name in PIPELINE_TASKS}
        summary = run_summary(_config(), _run_id(), reports)
        if not summary.succeeded:
            # This is the DAG's only leaf, so it must fail for the run to show as failed.
            raise RuntimeError(f"Pipeline stages failed: {', '.join(summary.failed_stages)}")
        return {"status": summary.status, "counts": summary.counts}

    extracted = extract()
    loaded = load(transform(extracted))
    finished = [commit_watermark(extracted, loaded), reconcile(extracted, loaded)]
    finished >> publish_run_status()


confluence_indexing()
