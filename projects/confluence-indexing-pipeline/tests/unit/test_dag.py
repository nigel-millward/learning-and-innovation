"""DAG structure check against a real Airflow 3 install (skipped where Airflow is absent)."""

from pathlib import Path

import pytest

pytest.importorskip("airflow.sdk")

import confluence_indexer

DAG_DIR = Path(confluence_indexer.__file__).parent


def _dagbag():
    from airflow.dag_processing.dagbag import DagBag

    # Scans the whole package, as AIRFLOW__CORE__DAGS_FOLDER does, so this also
    # checks .airflowignore keeps non-DAG modules out of parsing.
    bag = DagBag(dag_folder=str(DAG_DIR))
    assert bag.import_errors == {}
    assert set(bag.dags) == {"confluence_indexing"}
    return bag


def test_dag_parses_with_expected_shape():
    dag = _dagbag().dags["confluence_indexing"]  # get_dag() would need a metadata DB
    assert dag.max_active_runs == 1
    assert not dag.catchup

    upstream = {t.task_id: {u.task_id for u in t.upstream_list} for t in dag.tasks}
    assert upstream == {
        "schema_management": set(),
        "extract": {"schema_management"},
        "transform": {"extract"},
        "load": {"transform"},
        "commit_watermark": {"extract", "load"},
        "reconcile": {"extract", "load"},
        "publish_run_status": {"commit_watermark", "reconcile"},
    }
    assert dag.get_task("publish_run_status").trigger_rule == "all_done"
    assert {a.name for a in dag.get_task("load").outlets} == {"confluence_index"}


def test_reports_round_trip_through_xcom(monkeypatch):
    from confluence_indexer.orchestration import airflow_runtime

    class FakeTaskInstance:
        def __init__(self):
            self.xcom = {}
            self.task_id = "extract"

        def xcom_push(self, key, value):
            self.xcom[(self.task_id, key)] = value

        def xcom_pull(self, task_ids, key):
            return self.xcom.get((task_ids, key))

    ti = FakeTaskInstance()
    monkeypatch.setattr(airflow_runtime, "get_current_context", lambda: {"ti": ti})

    report = {"status": "success", "outputs": {"manifest_uri": "s3://b/m.json"}}
    airflow_runtime.push_report(report, "manifest_uri")

    assert airflow_runtime.pull_output("extract", "manifest_uri") == "s3://b/m.json"
    assert airflow_runtime.pull_reports(("extract", "load")) == {"extract": report, "load": None}
