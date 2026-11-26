"""Run the pipeline on your machine, without Airflow, while developing.

Calls the same ``run_*`` functions as the Airflow tasks, in DAG order, so you test
the code that runs in production. Not deployed: this file lives outside ``src/``.

Usage, from the project directory, after starting the local stack and loading .env
(see README, "Run it locally"):

    python scripts/run_pipeline_locally.py                       # create schema, then one run
    python scripts/run_pipeline_locally.py --full-refresh        # re-read every page
    python scripts/run_pipeline_locally.py --replay s3://.../extract_manifest.json
                                                                 # transform + load only
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from confluence_indexer.config import PipelineConfig
from confluence_indexer.orchestration.tasks import (
    run_commit_watermark,
    run_extract,
    run_load,
    run_reconcile,
    run_schema_management,
    run_summary,
    run_transform,
)

log = logging.getLogger("run_pipeline_locally")


def parse_args() -> argparse.Namespace:
    """Parse the command-line arguments.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Run the pipeline locally, without Airflow.")
    parser.add_argument("--full-refresh", action="store_true", help="ignore the load_date")
    parser.add_argument("--allow-mass-delete", action="store_true", help="bypass deletion guard")
    parser.add_argument(
        "--replay",
        metavar="MANIFEST_URI",
        help="re-run transform and load from a past run's extract_manifest.json, "
        "without calling Confluence",
    )
    parser.add_argument(
        "--skip-schema-management",
        action="store_true",
        help="do not create missing schema objects first",
    )
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def run_pipeline(config: PipelineConfig, run_id: str, args: argparse.Namespace) -> int:
    """Run every stage in DAG order.

    A failure stops the run, then the summary still runs.

    Args:
        config: Pipeline config.
        run_id: ID for this run.
        args: Parsed command-line arguments.

    Returns:
        Exit code: 0 if the run succeeded, otherwise 1.
    """
    reports: dict[str, dict[str, Any] | None] = {}
    try:
        extracted = reports["extract"] = run_extract(config, run_id, full_refresh=args.full_refresh)
        started_at = extracted["outputs"]["run_started_at"]
        transformed = reports["transform"] = run_transform(
            config, run_id, extracted["outputs"]["manifest_uri"]
        )
        reports["load"] = run_load(config, run_id, transformed["outputs"]["documents_uri"])
        reports["commit_watermark"] = run_commit_watermark(config, run_id, started_at)
        reports["reconcile"] = run_reconcile(
            config, run_id, started_at, allow_mass_delete=args.allow_mass_delete
        )
    except Exception:
        log.exception("Run %s stopped at a failed stage", run_id)
    summary = run_summary(config, run_id, reports)
    print(json.dumps({"status": summary.status, "counts": summary.counts}, indent=2))
    return 0 if summary.succeeded else 1


def replay(config: PipelineConfig, run_id: str, manifest_uri: str) -> int:
    """Re-run transform and load from a past extract manifest, without calling Confluence.

    Args:
        config: Pipeline config.
        run_id: ID for this replay run.
        manifest_uri: S3 URI of the past run's ``extract_manifest.json``.

    Returns:
        Exit code 0.
    """
    transformed = run_transform(config, run_id, manifest_uri)
    loaded = run_load(config, run_id, transformed["outputs"]["documents_uri"])
    print(json.dumps({"transform": transformed, "load": loaded}, indent=2, default=str))
    return 0


def main() -> int:
    """Create the schema unless skipped, then run the pipeline or a replay.

    Returns:
        The process exit code.
    """
    args = parse_args()
    logging.basicConfig(
        level=args.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    config = PipelineConfig.from_env()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    if not args.skip_schema_management:
        run_schema_management(config)
    if args.replay:
        return replay(config, f"local_replay__{stamp}", args.replay)
    return run_pipeline(config, f"local__{stamp}", args)


if __name__ == "__main__":
    sys.exit(main())
