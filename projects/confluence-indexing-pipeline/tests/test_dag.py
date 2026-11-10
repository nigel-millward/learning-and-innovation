"""DAG structure check against a real Airflow 3 install (skipped where Airflow is absent)."""

from pathlib import Path

import pytest

pytest.importorskip("airflow.sdk")

import confluence_indexer.dags as dags_package

DAG_DIR = Path(dags_package.__file__).parent


def test_dag_parses_with_expected_shape():
    from airflow.dag_processing.dagbag import DagBag

    bag = DagBag(dag_folder=str(DAG_DIR))
    assert bag.import_errors == {}
    dag = bag.dags["confluence_indexing"]  # get_dag() would need a metadata DB
    assert dag.max_active_runs == 1
    assert not dag.catchup

    upstream = {t.task_id: {u.task_id for u in t.upstream_list} for t in dag.tasks}
    assert upstream == {
        "extract": set(),
        "transform": {"extract"},
        "load": {"transform"},
        "commit_watermark": {"extract", "load"},
        "reconcile": {"extract", "load"},
        "publish_run_status": {"commit_watermark", "reconcile"},
    }
    assert dag.get_task("publish_run_status").trigger_rule == "all_done"
    assert {a.name for a in dag.get_task("load").outlets} == {"confluence_index"}
