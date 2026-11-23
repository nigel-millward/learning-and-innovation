"""
### Confluence indexing maintenance (manual trigger only)

* **migrate** - applies pending schema migrations, and is safe to repeat:
  migrations already applied are skipped. Trigger it to create the schema before
  the first `confluence_indexing` run, and after deploying a new migration.

To re-process a past run without calling Confluence, clear `transform` and `load`
on that `confluence_indexing` run (without downstream tasks); they re-read the
run's extract manifest from XCom.
"""

from __future__ import annotations

from datetime import timedelta

import pendulum
from airflow.sdk import dag, task

from confluence_indexer.orchestration.airflow_runtime import alert_task_failure, pipeline_config


@dag(
    dag_id="confluence_indexing_maintenance",
    schedule=None,
    start_date=pendulum.datetime(2026, 11, 1, tz="Europe/London"),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "data-engineering",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "execution_timeout": timedelta(minutes=30),
        "on_failure_callback": alert_task_failure,
    },
    tags=["confluence", "rag", "pgvector", "maintenance"],
    doc_md=__doc__,
)
def confluence_indexing_maintenance() -> None:
    @task
    def migrate() -> dict[str, list[str]]:
        from confluence_indexer.orchestration.tasks import run_migrate

        return run_migrate(pipeline_config())

    migrate()


confluence_indexing_maintenance()
