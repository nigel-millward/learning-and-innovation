"""Task entry points: wire each pipeline stage to real clients.

Each ``run_*`` function is the body of one Airflow task in ``confluence_indexing_dag.py``.
Each call builds its own clients and
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
from ..integrations.vector_store import PgVectorStore, apply_schema_management
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
    """Build a landing zone backed by a new S3 client.

    Args:
        config: Pipeline config supplying the AWS region and landing-zone settings.

    Returns:
        A ``LandingZone`` for the configured bucket.
    """
    return LandingZone(boto3.client("s3", region_name=config.aws_region), config.landing)


def _saved(config: PipelineConfig, run_id: str, report: StageReport) -> dict[str, Any]:
    """Persist the stage report next to the run's other artefacts, for audit.

    Args:
        config: Pipeline config.
        run_id: ID of the run the report belongs to.
        report: Stage report to save as ``<stage>_report.json``.

    Returns:
        The report as a dict.
    """
    data = report.to_dict()
    _landing(config).put_run_json(run_id, f"{report.stage}_report.json", data)
    log.info("%s report: %s", report.stage, data)
    return data


def run_extract(
    config: PipelineConfig, run_id: str, *, full_refresh: bool = False
) -> dict[str, Any]:
    """Run the extract stage: land raw payloads of changed Confluence pages in S3.

    Args:
        config: Pipeline config.
        run_id: ID of the current run.
        full_refresh: Whether to re-read every page, ignoring the load_date.

    Returns:
        The stage report as a dict, also saved to the landing zone.
    """
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
    """Run the transform stage: clean and chunk the extracted pages.

    Args:
        config: Pipeline config.
        run_id: ID of the current run.
        manifest_uri: S3 URI of the extract manifest to transform.

    Returns:
        The stage report as a dict, also saved to the landing zone.
    """
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
    """Run the load stage: embed new or changed chunks and write pages to pgvector.

    Args:
        config: Pipeline config.
        run_id: ID of the current run.
        documents_uri: S3 URI of the transformed documents to load.

    Returns:
        The stage report as a dict, also saved to the landing zone.
    """
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
    """Run the reconcile stage: remove vectors for pages deleted or hidden in Confluence.

    Args:
        config: Pipeline config.
        run_id: ID of the current run.
        run_started_at: ISO 8601 timestamp of when the run started.
        allow_mass_delete: Whether to bypass the mass-deletion guard.

    Returns:
        The stage report as a dict, also saved to the landing zone.
    """
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
    """Run the commit-watermark stage: advance the load_date to the run start.

    Args:
        config: Pipeline config.
        run_id: ID of the current run.
        run_started_at: ISO 8601 timestamp of when the run started.

    Returns:
        The stage report as a dict, also saved to the landing zone.
    """
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
    """Summarise the run, publish metrics and send alerts.

    If the database is unavailable, the summary is still built and metrics published,
    without a store.

    Args:
        config: Pipeline config.
        run_id: ID of the current run.
        reports: Each stage's report keyed by stage, or None for a stage that did not run.

    Returns:
        The run summary.
    """
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
    """Build an alerter that publishes to the configured SNS topic.

    Args:
        config: Pipeline config supplying the AWS region and alert topic.

    Returns:
        An ``Alerter`` for this pipeline and environment.
    """
    return Alerter(
        boto3.client("sns", region_name=config.aws_region),
        config.observability.alert_topic_arn,
        config.pipeline_name,
        config.environment,
    )


def run_schema_management(config: PipelineConfig) -> dict[str, Any]:
    """Create any missing schema objects.

    Safe to repeat: existing objects are kept.

    Args:
        config: Pipeline config supplying the database DSN and embedding dimensions.

    Returns:
        A dict with the schema scripts applied under ``"applied"``.
    """
    applied = apply_schema_management(
        config.database.database_connection_string, config.embedding.dimensions
    )
    log.info("Schema scripts applied: %s", applied)
    return {"applied": applied}
