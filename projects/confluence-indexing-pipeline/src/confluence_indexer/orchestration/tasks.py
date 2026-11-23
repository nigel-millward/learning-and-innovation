"""Task entry points: wire each pipeline stage to real clients.

Each ``run_*`` function is the body of one Airflow task in ``confluence_indexing_dag.py``
or ``confluence_indexing_maintenance_dag.py``. Each call builds its own clients and
connection: Airflow tasks may land on different workers, so nothing is shared
between stages except what is persisted in S3 and PostgreSQL.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Any

import boto3

from ..config import PipelineConfig
from ..integrations.confluence import ConfluenceClient
from ..integrations.embeddings import build_embedding_provider
from ..integrations.landing_zone import LandingZone
from ..integrations.observability import Alerter, MetricsPublisher
from ..integrations.vector_store import PgVectorStore, apply_migrations
from ..processing.chunking import Chunker
from ..processing.cleaning import StorageFormatCleaner
from ..stages import (
    RunSummary,
    StageReport,
    commit_watermark,
    extract,
    load,
    reconcile,
    summarise,
    transform,
)

log = logging.getLogger(__name__)


def _landing(config: PipelineConfig) -> LandingZone:
    return LandingZone(boto3.client("s3", region_name=config.aws_region), config.landing)


def _saved(config: PipelineConfig, run_id: str, report: StageReport) -> dict[str, Any]:
    """Persist the stage report next to the run's other artefacts, for audit."""
    data = report.to_dict()
    _landing(config).put_run_json(run_id, f"{report.stage}_report.json", data)
    log.info("%s report: %s", report.stage, data)
    return data


def run_extract(
    config: PipelineConfig, run_id: str, *, full_refresh: bool = False
) -> dict[str, Any]:
    with (
        ConfluenceClient(config.confluence) as confluence,
        PgVectorStore.connect(config.database.database_connection_string) as store,
    ):
        report = extract(
            config,
            confluence=confluence,
            landing=_landing(config),
            store=store,
            run_id=run_id,
            full_refresh=full_refresh,
        )
    return _saved(config, run_id, report)


def run_transform(config: PipelineConfig, run_id: str, manifest_uri: str) -> dict[str, Any]:
    with PgVectorStore.connect(config.database.database_connection_string) as store:
        report = transform(
            config,
            landing=_landing(config),
            store=store,
            cleaner=StorageFormatCleaner(config.chunking.boilerplate_patterns),
            chunker=Chunker(config.chunking),
            run_id=run_id,
            manifest_uri=manifest_uri,
        )
    return _saved(config, run_id, report)


def run_load(config: PipelineConfig, run_id: str, documents_uri: str) -> dict[str, Any]:
    with PgVectorStore.connect(config.database.database_connection_string) as store:
        report = load(
            config,
            landing=_landing(config),
            store=store,
            embedder=build_embedding_provider(config.embedding),
            run_id=run_id,
            documents_uri=documents_uri,
        )
    return _saved(config, run_id, report)


def run_reconcile(
    config: PipelineConfig, run_id: str, run_started_at: str, *, allow_mass_delete: bool = False
) -> dict[str, Any]:
    with (
        ConfluenceClient(config.confluence) as confluence,
        PgVectorStore.connect(config.database.database_connection_string) as store,
    ):
        report = reconcile(
            config,
            confluence=confluence,
            store=store,
            run_started_at=datetime.fromisoformat(run_started_at),
            allow_mass_delete=allow_mass_delete,
        )
    return _saved(config, run_id, report)


def run_commit_watermark(
    config: PipelineConfig, run_id: str, run_started_at: str
) -> dict[str, Any]:
    with PgVectorStore.connect(config.database.database_connection_string) as store:
        report = commit_watermark(
            config,
            store=store,
            run_id=run_id,
            run_started_at=datetime.fromisoformat(run_started_at),
        )
    return _saved(config, run_id, report)


def run_summary(
    config: PipelineConfig, run_id: str, reports: Mapping[str, Mapping[str, Any] | None]
) -> RunSummary:
    metrics = MetricsPublisher(
        boto3.client("cloudwatch", region_name=config.aws_region),
        config.observability.metrics_namespace,
        config.pipeline_name,
        config.environment,
    )
    try:
        with PgVectorStore.connect(config.database.database_connection_string) as store:
            return summarise(
                config,
                reports,
                run_id=run_id,
                store=store,
                metrics=metrics,
                alerter=alerter(config),
            )
    except Exception as exc:
        # The database may be the very thing that failed; metrics must still go out.
        log.warning("Database unavailable for run summary (%s); publishing metrics only", exc)
        return summarise(
            config, reports, run_id=run_id, store=None, metrics=metrics, alerter=alerter(config)
        )


def alerter(config: PipelineConfig) -> Alerter:
    return Alerter(
        boto3.client("sns", region_name=config.aws_region),
        config.observability.alert_topic_arn,
        config.pipeline_name,
        config.environment,
    )


def run_migrate(config: PipelineConfig) -> dict[str, Any]:
    """Apply pending schema migrations. Safe to repeat: applied files are skipped."""
    applied = apply_migrations(
        config.database.database_connection_string, config.embedding.dimensions
    )
    log.info("Migrations applied: %s", applied or "none pending")
    return {"applied": applied}
