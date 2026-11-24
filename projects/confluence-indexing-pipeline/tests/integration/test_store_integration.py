"""PgVectorStore against a real PostgreSQL + pgvector.

Run with the local stack:  docker compose -f deployment/docker-compose.yml up -d
    PGVECTOR_TEST_DSN=postgresql://indexer:indexer@localhost:5433/postgres pytest -m integration

Each test runs in a freshly created database, so the suite is safe to repeat.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import psycopg
import pytest

from confluence_indexer.integrations.vector_store import (
    PgVectorStore,
    SchemaMismatchError,
    apply_schema_management,
)
from confluence_indexer.models import Chunk, PageDocument, PageMetadata

DSN = os.environ.get("PGVECTOR_TEST_DSN")
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not DSN, reason="PGVECTOR_TEST_DSN not set"),
]

DIMS = 768  # Ollama nomic-embed-text, the local default
EV = f"ollama:nomic-embed-text:{DIMS}:r1"
T0 = datetime(2026, 11, 1, tzinfo=UTC)


@pytest.fixture
def empty_dsn() -> Iterator[str]:
    assert DSN
    name = f"indexer_test_{uuid.uuid4().hex[:12]}"
    with psycopg.connect(DSN, autocommit=True) as admin:
        admin.execute(f'CREATE DATABASE "{name}"')
    try:
        yield psycopg.conninfo.make_conninfo(DSN, dbname=name)
    finally:
        with psycopg.connect(DSN, autocommit=True) as admin:
            admin.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')


@pytest.fixture
def dsn(empty_dsn: str) -> str:
    apply_schema_management(empty_dsn, DIMS)
    return empty_dsn


@pytest.fixture
def store(dsn: str) -> Iterator[PgVectorStore]:
    with PgVectorStore.connect(dsn) as s:
        yield s


def document(page_id: str, texts: list[str], version: int = 1) -> PageDocument:
    meta = PageMetadata(
        page_id=page_id,
        space_key="ENG",
        space_name="Engineering",
        title=f"Page {page_id}",
        url=f"https://example/wiki/{page_id}",
        version=version,
        last_modified=T0,
        last_modified_by="Ada",
        labels=("a",),
        ancestors=("Home",),
    )
    chunks = tuple(
        Chunk(page_id, i, text, f"Title: Page {page_id}\n\n{text}", 5, ("Intro",))
        for i, text in enumerate(texts)
    )
    return PageDocument(meta, f"s3://b/raw/{page_id}/{version}.json", chunks)


def vectors_for(doc: PageDocument) -> dict[str, list[float]]:
    # Orthogonal unit vectors, so cosine nearest-neighbour results are unambiguous.
    return {
        c.content_hash: [1.0 if j == c.chunk_index else 0.0 for j in range(DIMS)]
        for c in doc.chunks
    }


def test_schema_management_reruns_without_losing_data(store: PgVectorStore, dsn: str) -> None:
    store.advance_load_date("p", T0, "r1")
    apply_schema_management(dsn, DIMS)
    assert store.get_load_date("p") == T0
    store.check_schema(DIMS)


def test_schema_management_renames_legacy_watermark_column(empty_dsn: str) -> None:
    with psycopg.connect(empty_dsn, autocommit=True) as conn:
        conn.execute("CREATE SCHEMA confluence_index")
        conn.execute(
            "CREATE TABLE confluence_index.pipeline_state (pipeline_name text PRIMARY KEY, "
            "watermark timestamptz NOT NULL, last_run_id text NOT NULL, "
            "updated_at timestamptz NOT NULL DEFAULT now())"
        )
        conn.execute("INSERT INTO confluence_index.pipeline_state VALUES ('p', %s, 'r1')", [T0])
    apply_schema_management(empty_dsn, DIMS)
    with PgVectorStore.connect(empty_dsn) as store:
        assert store.get_load_date("p") == T0


def test_schema_dimension_check(store: PgVectorStore) -> None:
    store.check_schema(DIMS)
    with pytest.raises(SchemaMismatchError):
        store.check_schema(1536)


def test_watermark_only_moves_forward(store: PgVectorStore) -> None:
    assert store.get_load_date("p") is None
    store.advance_load_date("p", T0 + timedelta(days=1), "r1")
    assert store.advance_load_date("p", T0, "r2") == T0 + timedelta(days=1)


def test_upsert_replace_and_reuse(store: PgVectorStore) -> None:
    doc = document("1", ["alpha", "beta", "gamma"])
    assert store.upsert_page(doc, vectors_for(doc), EV) == 0

    indexed = store.get_indexed_pages(["1", "missing"])
    assert indexed["1"].content_hash == doc.content_hash
    assert indexed["1"].embedding_version == EV

    found = store.find_embeddings([c.content_hash for c in doc.chunks] + ["nope"], EV)
    assert set(found) == {c.content_hash for c in doc.chunks}
    assert store.find_embeddings([doc.chunks[0].content_hash], "other-version") == {}

    shorter = document("1", ["alpha"], version=2)
    assert store.upsert_page(shorter, vectors_for(shorter), EV) == 2
    assert store.get_indexed_pages(["1"])["1"].version == 2


def test_similarity_search_uses_stored_vectors(store: PgVectorStore, dsn: str) -> None:
    doc = document("1", ["alpha", "beta"])
    store.upsert_page(doc, vectors_for(doc), EV)
    with psycopg.connect(dsn) as conn:
        row = conn.execute(
            "SELECT chunk_id, metadata->>'title' FROM confluence_index.chunks "
            "ORDER BY embedding <=> (SELECT embedding FROM confluence_index.chunks "
            "WHERE chunk_index = 1) LIMIT 1"
        ).fetchone()
    assert row == ("1:00001", "Page 1")


def test_deletion_soft_deletes_page_and_removes_vectors(store: PgVectorStore) -> None:
    doc = document("1", ["alpha", "beta"])
    store.upsert_page(doc, vectors_for(doc), EV)
    store.record_failure("1", "load", RuntimeError("x"), "r1")

    assert store.list_active_page_ids(indexed_before=datetime.now(UTC) + timedelta(minutes=1)) == {
        "1"
    }
    assert store.mark_pages_deleted(["1"]) == (1, 2)
    assert store.get_indexed_pages(["1"]) == {}
    assert store.count_active_pages() == 0
    assert store.retryable_failures(5) == []

    # Re-indexing a deleted page reactivates it.
    store.upsert_page(doc, vectors_for(doc), EV)
    assert store.count_active_pages() == 1


def test_dead_letter_attempts(store: PgVectorStore) -> None:
    for _ in range(3):
        store.record_failure("9", "extract", RuntimeError("boom"), "r")
    assert store.retryable_failures(3) == []
    assert store.retryable_failures(4) == ["9"]
    assert store.count_parked_failures(3) == 1
    store.clear_failures(["9"])
    assert store.count_parked_failures(1) == 0


def test_record_run(store: PgVectorStore) -> None:
    store.record_run("p", "r1", "failed", {"RunFailed": 1}, ["load"])
    store.record_run("p", "r1", "success", {"RunSucceeded": 1}, [])
