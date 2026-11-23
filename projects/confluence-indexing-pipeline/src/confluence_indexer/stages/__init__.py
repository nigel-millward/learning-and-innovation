"""Pipeline stages, one module each, in DAG order.

Pure functions of their inputs and collaborators; no Airflow imports. The DAGs
(``confluence_indexer/*_dag.py``) reach them through ``orchestration.tasks``.
"""

from .base import STAGES, DeletionGuardError, StageFailedError, StageReport
from .extract import extract
from .load import load
from .reconcile import reconcile
from .summary import RunSummary, summarise
from .transform import transform
from .watermark import commit_watermark

__all__ = [
    "STAGES",
    "DeletionGuardError",
    "RunSummary",
    "StageFailedError",
    "StageReport",
    "commit_watermark",
    "extract",
    "load",
    "reconcile",
    "summarise",
    "transform",
]
