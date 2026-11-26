"""Airflow runtime helpers for the DAGs: config, run context, XCom and failure alerts.

Keeps Airflow plumbing out of the ``*_dag.py`` files so they only describe tasks
and their order. The DAG processor imports this module every time it parses a
DAG, so pipeline dependencies are imported lazily inside functions, never at
module level.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

from airflow.sdk import Connection, get_current_context
from airflow.sdk.exceptions import AirflowNotFoundException

if TYPE_CHECKING:
    from ..config import PipelineConfig

log = logging.getLogger(__name__)

# XCom key every stage pushes its full report under; publish_run_status pulls them all.
REPORT_KEY = "report"

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


def pipeline_config() -> PipelineConfig:
    """Build pipeline config from the environment, overlaid with Airflow Connections.

    Each Connection in ``CONNECTION_ENV`` that exists overrides the matching environment
    variables; missing Connections are skipped. A Confluence host without a scheme gets
    ``https://`` prepended.

    Returns:
        The pipeline config built from the merged environment.
    """
    from ..config import PipelineConfig

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


def run_id() -> str:
    """Return the current DAG run's ID.

    Returns:
        The ``run_id`` from the current Airflow task context.
    """
    return str(get_current_context()["run_id"])


def bool_param(name: str) -> bool:
    """Return a DAG run param as a bool.

    Args:
        name: Name of the param in the current task context.

    Returns:
        The truthiness of the param's value.
    """
    return bool(get_current_context()["params"][name])


def push_report(report: dict[str, Any], *output_keys: str) -> None:
    """Push a stage report, plus the named entries from its outputs under their own keys.

    Call this last in a task, so a task that fails pushes nothing.

    Args:
        report: Stage report dict, pushed under ``REPORT_KEY``.
        *output_keys: Keys of ``report["outputs"]`` to also push under their own XCom keys.
    """
    ti = get_current_context()["ti"]
    ti.xcom_push(key=REPORT_KEY, value=report)
    for key in output_keys:
        ti.xcom_push(key=key, value=report["outputs"][key])


def pull_output(task_id: str, key: str) -> Any:
    """Pull an XCom value pushed by another task in the current run.

    Args:
        task_id: ID of the task that pushed the value.
        key: XCom key the value was pushed under.

    Returns:
        The pushed value, or None if nothing was pushed.
    """
    return get_current_context()["ti"].xcom_pull(task_ids=task_id, key=key)


def pull_reports(task_ids: tuple[str, ...]) -> dict[str, dict[str, Any] | None]:
    """Pull the stage report pushed by each of the given tasks.

    Args:
        task_ids: IDs of the tasks whose reports to pull.

    Returns:
        Each task's report keyed by task ID, or None for a task that failed or was skipped.
    """
    return {task_id: pull_output(task_id, REPORT_KEY) for task_id in task_ids}


def alert_task_failure(context: dict[str, Any]) -> None:
    """Send an SNS alert when a task fails after exhausting its retries.

    Used as an ``on_failure_callback``. Any error while alerting is logged, not raised.

    Args:
        context: Airflow task context passed to the callback.
    """
    try:
        from .tasks import alerter

        ti = context["task_instance"]
        alerter(pipeline_config()).send(
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
