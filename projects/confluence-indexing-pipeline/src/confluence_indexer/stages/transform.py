"""Transform: clean storage-format XHTML and chunk it, staging JSONL in S3."""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

from ..config import PipelineConfig
from ..integrations.landing_zone import LandingZone
from ..integrations.vector_store import PgVectorStore
from ..models import PageDocument, PageMetadata
from ..processing.chunking import Chunker
from ..processing.cleaning import StorageFormatCleaner
from .base import StageReport, enforce_failure_budget, page_failed


def transform(
    config: PipelineConfig,
    *,
    landing: LandingZone,
    store: PgVectorStore,
    cleaner: StorageFormatCleaner,
    chunker: Chunker,
    run_id: str,
    manifest_uri: str,
) -> StageReport:
    """Clean and chunk every landed page into a staged JSONL file."""
    started = time.monotonic()
    report = StageReport("transform")
    manifest = landing.get_json(manifest_uri)

    def documents() -> Iterator[dict[str, Any]]:
        for ref in manifest["pages"]:
            try:
                payload = landing.get_raw_page(ref["raw_uri"])
                meta = PageMetadata.from_api(payload, config.confluence.base_url)
                storage = ((payload.get("body") or {}).get("storage") or {}).get("value", "")
                text = cleaner.clean(storage, meta.title)
                chunks = chunker.chunk(meta, text)
            except Exception as exc:
                page_failed(store, report, ref["page_id"], exc, run_id)
                continue
            report.counts["pages_transformed"] += 1
            report.counts["chunks_produced"] += len(chunks)
            if not chunks:
                report.counts["pages_empty"] += 1
            yield PageDocument(
                metadata=meta, raw_uri=ref["raw_uri"], chunks=tuple(chunks)
            ).to_dict()

    documents_uri = landing.put_run_jsonl(run_id, "documents.jsonl", documents())
    report.outputs = {"documents_uri": documents_uri}
    enforce_failure_budget(config, report, attempted=len(manifest["pages"]))
    report.seconds = time.monotonic() - started
    return report
