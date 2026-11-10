"""Task entry points: wire each pipeline stage to real clients.

Each ``run_*`` function is the body of one Airflow task in
``dags/confluence_indexing.py``; the CLI calls the same functions, so a stage
behaves identically on an Airflow worker and on a laptop. Each call builds its own clients and
connection: Airflow tasks may land on different workers, so nothing is shared
between stages except what is persisted in S3 and PostgreSQL.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Any

import boto3

from .config import PipelineConfig
from .integrations.confluence import ConfluenceClient
from .integrations.embeddings import build_embedding_provider
from .integrations.landing_zone import LandingZone
from .integrations.observability import Alerter, MetricsPublisher
from .integrations.vector_store import PgVectorStore
from .processing.chunking import Chunker
from .processing.cleaning import StorageFormatCleaner
from .stages import (
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
        PgVectorStore.connect(config.database.dsn) as store,
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
    with PgVectorStore.connect(config.database.dsn) as store:
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
    with PgVectorStore.connect(config.database.dsn) as store:
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
        PgVectorStore.connect(config.database.dsn) as store,
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
    with PgVectorStore.connect(config.database.dsn) as store:
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
        with PgVectorStore.connect(config.database.dsn) as store:
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


def run_all(
    config: PipelineConfig,
    run_id: str,
    *,
    full_refresh: bool = False,
    allow_mass_delete: bool = False,
) -> RunSummary:
    """Run every stage in-process, in DAG order. For local runs and backfills."""
    reports: dict[str, dict[str, Any] | None] = {}
    try:
        extracted = reports["extract"] = run_extract(config, run_id, full_refresh=full_refresh)
        started = extracted["outputs"]["run_started_at"]
        transformed = reports["transform"] = run_transform(
            config, run_id, extracted["outputs"]["manifest_uri"]
        )
        reports["load"] = run_load(config, run_id, transformed["outputs"]["documents_uri"])
        reports["commit_watermark"] = run_commit_watermark(config, run_id, started)
        reports["reconcile"] = run_reconcile(
            config, run_id, started, allow_mass_delete=allow_mass_delete
        )
    except Exception as exc:
        log.exception("Run %s failed", run_id)
        alerter(config).send("CRITICAL", "Run failed", {"run_id": run_id, "error": repr(exc)})
    return run_summary(config, run_id, reports)
