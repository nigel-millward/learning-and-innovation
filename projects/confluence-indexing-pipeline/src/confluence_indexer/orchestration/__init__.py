"""Runs the pipeline stages under Airflow.

    tasks.py            one run_* function per task; builds real clients (no Airflow imports)
    airflow_runtime.py  Airflow plumbing for the DAGs: config, run context, XCom keys, alerts

The DAG files themselves are ``confluence_indexer/*_dag.py``. Kept free of
imports: the DAG processor imports this package on every parse.
"""
