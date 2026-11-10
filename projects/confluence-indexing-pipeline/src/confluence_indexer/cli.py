"""Command line entry point for local runs, backfills, replays and migrations.

Airflow is the scheduler in every deployed environment (see dags/); this CLI
runs the same task functions in-process for local development and operations.

confluence-indexer migrate
confluence-indexer run [--full-refresh] [--allow-mass-delete]
confluence-indexer replay s3://bucket/prefix/runs/run_id=.../extract_manifest.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import UTC, datetime

from .config import PipelineConfig
from .integrations.vector_store import apply_migrations
from .tasks import run_all, run_load, run_transform


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="confluence-indexer")
    parser.add_argument("--log-level", default="INFO")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser(
        "migrate", help="apply database migrations (vector size from EMBEDDING_DIMENSIONS)"
    )

    run = commands.add_parser("run", help="run every stage once, in-process")
    run.add_argument("--run-id", default=None)
    run.add_argument("--full-refresh", action="store_true", help="ignore the watermark")
    run.add_argument("--allow-mass-delete", action="store_true")

    replay = commands.add_parser(
        "replay", help="re-run transform and load from landed raw pages, without calling Confluence"
    )
    replay.add_argument("manifest_uri", help="S3 URI of a run's extract_manifest.json")
    replay.add_argument("--run-id", default=None)

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    config = PipelineConfig.from_env()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    if args.command == "migrate":
        applied = apply_migrations(config.database.dsn, config.embedding.dimensions)
        print(json.dumps({"applied": applied}))
        return 0

    if args.command == "replay":
        run_id = args.run_id or f"replay__{stamp}"
        transformed = run_transform(config, run_id, args.manifest_uri)
        loaded = run_load(config, run_id, transformed["outputs"]["documents_uri"])
        print(json.dumps({"transform": transformed, "load": loaded}, indent=2))
        return 0

    summary = run_all(
        config,
        args.run_id or f"manual__{stamp}",
        full_refresh=args.full_refresh,
        allow_mass_delete=args.allow_mass_delete,
    )
    print(
        json.dumps(
            {
                "status": summary.status,
                "failed_stages": summary.failed_stages,
                "counts": summary.counts,
                "seconds": summary.seconds,
            },
            indent=2,
        )
    )
    return 0 if summary.succeeded else 1


if __name__ == "__main__":
    sys.exit(main())
