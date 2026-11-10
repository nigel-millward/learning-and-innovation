from __future__ import annotations

import hashlib
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any

import boto3
import pytest
from moto import mock_aws

from confluence_indexer.config import (
    ChunkingConfig,
    ConfluenceConfig,
    DatabaseConfig,
    EmbeddingConfig,
    GuardrailConfig,
    LandingConfig,
    ObservabilityConfig,
    PipelineConfig,
)
from confluence_indexer.integrations.confluence import PageHit
from confluence_indexer.integrations.landing_zone import LandingZone
from confluence_indexer.models import IndexedPage, PageDocument

DIMENSIONS = 8
BUCKET = "test-landing"


@pytest.fixture
def config() -> PipelineConfig:
    return PipelineConfig(
        pipeline_name="confluence-indexing",
        environment="test",
        aws_region="eu-west-2",
        confluence=ConfluenceConfig(
            base_url="https://example.atlassian.net/wiki",
            api_token="token",
            username="svc@example.com",
            space_keys=("ENG",),
        ),
        landing=LandingConfig(bucket=BUCKET, prefix="confluence-indexing"),
        chunking=ChunkingConfig(chunk_size_tokens=120, chunk_overlap_tokens=15),
        embedding=EmbeddingConfig(
            provider="openai", model="text-embedding-3-large", dimensions=DIMENSIONS, api_key="k"
        ),
        database=DatabaseConfig(dsn="postgresql://unused"),
        observability=ObservabilityConfig(),
        guardrails=GuardrailConfig(
            watermark_overlap=timedelta(minutes=30), mass_delete_min_pages=1, load_batch_pages=2
        ),
    )


@pytest.fixture
def landing(config: PipelineConfig) -> Iterator[LandingZone]:
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-west-2")
        s3.create_bucket(
            Bucket=BUCKET, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
        )
        yield LandingZone(s3, config.landing)


def page_payload(
    page_id: str,
    body: str,
    *,
    version: int = 1,
    title: str | None = None,
    space: str = "ENG",
    when: datetime | None = None,
) -> dict[str, Any]:
    when = when or datetime(2026, 11, 1, 9, 0, tzinfo=UTC)
    return {
        "id": page_id,
        "type": "page",
        "status": "current",
        "title": title or f"Page {page_id}",
        "space": {"key": space, "name": "Engineering"},
        "version": {"number": version, "when": when.isoformat(), "by": {"displayName": "Ada"}},
        "ancestors": [{"id": "1", "title": "Engineering Home"}],
        "metadata": {"labels": {"results": [{"name": "runbook"}]}},
        "body": {"storage": {"value": body, "representation": "storage"}},
        "_links": {
            "webui": f"/spaces/{space}/pages/{page_id}",
            "base": "https://example.atlassian.net/wiki",
        },
    }


class FakeConfluence:
    """In-memory Confluence: pages keyed by ID, with lastmodified for CQL filtering."""

    def __init__(self) -> None:
        self.pages: dict[str, dict[str, Any]] = {}
        self.searches: list[datetime | None] = []
        self.fetches: list[str] = []
        self.broken: set[str] = set()

    def put(self, payload: dict[str, Any]) -> None:
        self.pages[payload["id"]] = payload

    def changed_pages(self, since: datetime | None) -> Iterator[PageHit]:
        self.searches.append(since)
        for page_id, payload in sorted(self.pages.items()):
            when = datetime.fromisoformat(payload["version"]["when"])
            if since is None or when >= since:
                yield PageHit(page_id, payload["version"]["number"])

    def get_page(self, page_id: str) -> dict[str, Any] | None:
        self.fetches.append(page_id)
        if page_id in self.broken:
            raise RuntimeError("boom")
        return self.pages.get(page_id)

    def list_page_ids(self) -> set[str]:
        return set(self.pages)


class FakeEmbedder:
    dimensions = DIMENSIONS

    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self.poison: set[str] = set()  # substrings that make embedding fail

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        if any(marker in text for text in texts for marker in self.poison):
            raise RuntimeError("embedding rejected input")
        return [_vector(text) for text in texts]

    @property
    def embedded_texts(self) -> list[str]:
        return [text for call in self.calls for text in call]


def _vector(text: str) -> list[float]:
    digest = hashlib.sha256(text.encode()).digest()
    return [b / 255 for b in digest[:DIMENSIONS]]


class FakeStore:
    """Mirrors PgVectorStore's behaviour closely enough to exercise the stages."""

    def __init__(self) -> None:
        self.watermark: datetime | None = None
        self.pages: dict[str, dict[str, Any]] = {}
        self.chunks: dict[str, dict[str, Any]] = {}  # chunk_id -> row
        self.failures: dict[str, dict[str, Any]] = {}
        self.runs: list[dict[str, Any]] = []
        self.clock = datetime(2026, 11, 1, tzinfo=UTC)

    def check_schema(self, dimensions: int) -> None:
        assert dimensions == DIMENSIONS

    def get_watermark(self, pipeline: str) -> datetime | None:
        return self.watermark

    def advance_watermark(self, pipeline: str, watermark: datetime, run_id: str) -> datetime:
        self.watermark = max(filter(None, [self.watermark, watermark]))
        return self.watermark

    def get_indexed_pages(self, page_ids: Sequence[str]) -> dict[str, IndexedPage]:
        return {
            pid: IndexedPage(pid, row["version"], row["content_hash"], row["embedding_version"])
            for pid, row in self.pages.items()
            if pid in page_ids and row["status"] == "active"
        }

    def find_embeddings(self, hashes: Iterable[str], embedding_version: str) -> dict[str, Any]:
        wanted = set(hashes)
        return {
            row["content_hash"]: row["embedding"]
            for row in self.chunks.values()
            if row["content_hash"] in wanted and row["embedding_version"] == embedding_version
        }

    def upsert_page(
        self, document: PageDocument, vectors: Mapping[str, Any], embedding_version: str
    ) -> int:
        self.pages[document.page_id] = {
            "version": document.metadata.version,
            "title": document.metadata.title,
            "content_hash": document.content_hash,
            "embedding_version": embedding_version,
            "status": "active",
            "indexed_at": self.clock,
        }
        for chunk in document.chunks:
            self.chunks[chunk.chunk_id] = {
                "page_id": chunk.page_id,
                "chunk_index": chunk.chunk_index,
                "content_hash": chunk.content_hash,
                "embedding_version": embedding_version,
                "embedding": list(vectors[chunk.content_hash]),
                "text": chunk.text,
            }
        stale = [
            cid
            for cid, row in self.chunks.items()
            if row["page_id"] == document.page_id and row["chunk_index"] >= len(document.chunks)
        ]
        for cid in stale:
            del self.chunks[cid]
        return len(stale)

    def touch_page(self, document: PageDocument) -> None:
        self.pages[document.page_id]["version"] = document.metadata.version

    def list_active_page_ids(self, indexed_before: datetime) -> set[str]:
        return {
            pid
            for pid, row in self.pages.items()
            if row["status"] == "active" and row["indexed_at"] < indexed_before
        }

    def count_active_pages(self) -> int:
        return sum(1 for row in self.pages.values() if row["status"] == "active")

    def mark_pages_deleted(self, page_ids: Iterable[str]) -> tuple[int, int]:
        ids = set(page_ids)
        doomed = [cid for cid, row in self.chunks.items() if row["page_id"] in ids]
        for cid in doomed:
            del self.chunks[cid]
        pages = 0
        for pid in ids:
            if self.pages.get(pid, {}).get("status") == "active":
                self.pages[pid] = {**self.pages[pid], "status": "deleted"}
                pages += 1
            self.failures.pop(pid, None)
        return pages, len(doomed)

    def record_failure(self, page_id: str, stage: str, error: BaseException, run_id: str) -> None:
        current = self.failures.get(page_id, {"attempts": 0})
        self.failures[page_id] = {
            "stage": stage,
            "attempts": current["attempts"] + 1,
            "error": str(error),
        }

    def clear_failures(self, page_ids: Iterable[str]) -> None:
        for pid in page_ids:
            self.failures.pop(pid, None)

    def retryable_failures(self, max_attempts: int) -> list[str]:
        return sorted(pid for pid, f in self.failures.items() if f["attempts"] < max_attempts)

    def count_parked_failures(self, max_attempts: int) -> int:
        return sum(1 for f in self.failures.values() if f["attempts"] >= max_attempts)

    def record_run(self, pipeline: str, run_id: str, status: str, stats: Any, failed: Any) -> None:
        self.runs.append({"run_id": run_id, "status": status, "failed_stages": list(failed)})

    def page_chunks(self, page_id: str) -> list[dict[str, Any]]:
        rows = [row for row in self.chunks.values() if row["page_id"] == page_id]
        return sorted(rows, key=lambda row: row["chunk_index"])


@pytest.fixture
def confluence() -> FakeConfluence:
    return FakeConfluence()


@pytest.fixture
def store() -> FakeStore:
    return FakeStore()


@pytest.fixture
def embedder() -> FakeEmbedder:
    return FakeEmbedder()


def with_embedding_revision(config: PipelineConfig, revision: str) -> PipelineConfig:
    return replace(config, embedding=replace(config.embedding, revision=revision))
