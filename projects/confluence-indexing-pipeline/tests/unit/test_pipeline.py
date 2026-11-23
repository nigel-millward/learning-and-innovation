from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest

from confluence_indexer.config import PipelineConfig
from confluence_indexer.integrations.landing_zone import LandingZone
from confluence_indexer.processing.chunking import Chunker
from confluence_indexer.processing.cleaning import StorageFormatCleaner
from confluence_indexer.stages import (
    DeletionGuardError,
    StageFailedError,
    commit_watermark,
    extract,
    load,
    reconcile,
    summarise,
    transform,
)

from ..conftest import (
    FakeConfluence,
    FakeEmbedder,
    FakeStore,
    page_payload,
    with_embedding_revision,
)

DAY_1 = datetime(2026, 11, 2, 2, 0, tzinfo=UTC)
DAY_2 = DAY_1 + timedelta(days=1)

SECTIONS = "".join(
    f"<h2>Section {n}</h2>"
    + "".join(
        f"<p>{f'Paragraph {p} of section {n} explains the deployment process. ' * 4}</p>"
        for p in range(1, 3)
    )
    for n in range(1, 4)
)


def run(
    config: PipelineConfig,
    *,
    confluence: FakeConfluence,
    landing: LandingZone,
    store: FakeStore,
    embedder: FakeEmbedder,
    now: datetime,
    full_refresh: bool = False,
) -> dict[str, Any]:
    run_id = f"scheduled__{now.isoformat()}"
    store.clock = now + timedelta(seconds=1)  # rows written during the run
    reports = {
        "extract": extract(
            config,
            confluence=confluence,
            landing=landing,
            store=store,
            run_id=run_id,
            full_refresh=full_refresh,
            now=now,
        )
    }
    reports["transform"] = transform(
        config,
        landing=landing,
        store=store,
        cleaner=StorageFormatCleaner(),
        chunker=Chunker(config.chunking),
        run_id=run_id,
        manifest_uri=reports["extract"].outputs["manifest_uri"],
    )
    reports["load"] = load(
        config,
        landing=landing,
        store=store,
        embedder=embedder,
        run_id=run_id,
        documents_uri=reports["transform"].outputs["documents_uri"],
    )
    reports["commit_watermark"] = commit_watermark(
        config, store=store, run_id=run_id, run_started_at=now
    )
    return reports


@pytest.fixture
def env(config, confluence, landing, store, embedder):
    def _run(now: datetime, **kwargs: Any) -> dict[str, Any]:
        return run(
            config,
            confluence=confluence,
            landing=landing,
            store=store,
            embedder=embedder,
            now=now,
            **kwargs,
        )

    return _run


def test_first_run_indexes_everything_and_sets_watermark(env, confluence, store, embedder):
    confluence.put(page_payload("100", SECTIONS))
    confluence.put(page_payload("200", "<p>A short page about on-call rotas.</p>"))

    reports = env(DAY_1)

    assert confluence.searches == [None]
    assert reports["load"].counts["pages_indexed"] == 2
    assert store.load_date == DAY_1
    chunks = store.page_chunks("100")
    assert len(chunks) > 1
    assert len(embedder.embedded_texts) == len({c["content_hash"] for c in store.chunks.values()})
    assert all(text.startswith("Title: Page") for text in embedder.embedded_texts)


def test_incremental_run_uses_watermark_with_overlap_and_skips_unchanged(
    env, config, confluence, embedder
):
    # Edited just before run 1, so it falls inside run 2's overlap window.
    confluence.put(page_payload("100", SECTIONS, when=DAY_1 - timedelta(minutes=10)))
    confluence.put(page_payload("200", "<p>Old page.</p>"))
    env(DAY_1)
    embedder.calls.clear()
    confluence.fetches.clear()

    reports = env(DAY_2)

    assert confluence.searches[-1] == DAY_1 - config.guardrails.load_date_overlap
    # Page 100 is returned again by the overlap, but that version is already indexed.
    assert reports["extract"].counts["pages_changed"] == 1
    assert reports["extract"].counts["pages_already_indexed"] == 1
    assert confluence.fetches == []
    assert embedder.calls == []


def test_edit_reembeds_only_changed_chunks(env, confluence, store, embedder):
    confluence.put(page_payload("100", SECTIONS))
    env(DAY_1)
    before = {c["chunk_index"]: c["content_hash"] for c in store.page_chunks("100")}
    embedder.calls.clear()

    edited = SECTIONS.replace("Paragraph 1 of section 3", "Paragraph ONE of section 3")
    confluence.put(page_payload("100", edited, version=2, when=DAY_1 + timedelta(hours=3)))
    reports = env(DAY_2)

    after = {c["chunk_index"]: c["content_hash"] for c in store.page_chunks("100")}
    changed = {i for i in after if before.get(i) != after[i]}
    assert 0 < len(changed) < len(after)
    assert len(embedder.embedded_texts) == len(changed)
    assert reports["load"].counts["chunks_reused"] == len(after) - len(changed)
    assert store.pages["100"]["version"] == 2


def test_new_version_with_identical_text_only_touches_page(env, confluence, store, embedder):
    confluence.put(page_payload("100", SECTIONS))
    env(DAY_1)
    embedder.calls.clear()

    # e.g. a TOC macro was added: a new version, but nothing indexable changed.
    body = '<ac:structured-macro ac:name="toc"/>' + SECTIONS
    confluence.put(page_payload("100", body, version=2, when=DAY_1 + timedelta(hours=1)))
    reports = env(DAY_2)

    assert reports["load"].counts["pages_content_unchanged"] == 1
    assert embedder.calls == []
    assert store.pages["100"]["version"] == 2


def test_title_change_reembeds_because_header_is_embedded(env, confluence, embedder):
    confluence.put(page_payload("100", "<p>Body text that does not change.</p>"))
    env(DAY_1)
    embedder.calls.clear()

    confluence.put(
        page_payload(
            "100",
            "<p>Body text that does not change.</p>",
            version=2,
            title="Renamed",
            when=DAY_1 + timedelta(hours=1),
        )
    )
    env(DAY_2)

    assert len(embedder.embedded_texts) == 1
    assert embedder.embedded_texts[0].startswith("Title: Renamed")


def test_shrinking_page_deletes_trailing_chunks(env, confluence, store):
    confluence.put(page_payload("100", SECTIONS))
    env(DAY_1)
    assert len(store.page_chunks("100")) > 1

    confluence.put(
        page_payload("100", "<p>Now tiny.</p>", version=2, when=DAY_1 + timedelta(hours=1))
    )
    reports = env(DAY_2)

    assert len(store.page_chunks("100")) == 1
    assert reports["load"].counts["chunks_deleted"] > 0


def test_embedding_version_change_forces_refetch_and_reembed(
    config, confluence, landing, store, embedder
):
    confluence.put(page_payload("100", "<p>Stable text.</p>", when=DAY_1 - timedelta(minutes=5)))
    run(config, confluence=confluence, landing=landing, store=store, embedder=embedder, now=DAY_1)
    embedder.calls.clear()

    # Same Confluence version, but indexed under a different embedding version.
    bumped = with_embedding_revision(config, "2")
    run(bumped, confluence=confluence, landing=landing, store=store, embedder=embedder, now=DAY_2)

    assert len(embedder.embedded_texts) == 1
    assert store.pages["100"]["embedding_version"].endswith(":r2")


def test_full_refresh_reuses_existing_embeddings(env, confluence, embedder):
    confluence.put(page_payload("100", SECTIONS))
    env(DAY_1)
    embedder.calls.clear()

    reports = env(DAY_2, full_refresh=True)

    assert reports["extract"].counts["pages_extracted"] == 1
    assert embedder.calls == []


def test_failed_fetch_is_dead_lettered_and_retried_next_run(env, config, confluence, store):
    for n in range(1, 21):
        confluence.put(page_payload(str(n), f"<p>Page number {n}.</p>"))
    confluence.broken.add("7")

    reports = env(DAY_1)

    assert reports["extract"].counts["pages_failed"] == 1
    assert store.failures["7"]["stage"] == "extract"
    assert store.load_date == DAY_1  # one bad page does not hold back everyone else

    confluence.broken.clear()
    confluence.fetches.clear()
    env(DAY_2)

    assert confluence.fetches == ["7"]
    assert "7" not in store.failures
    assert "7" in store.pages


def test_poison_chunk_fails_only_its_page(env, config, confluence, store, embedder):
    for n in range(1, 21):
        confluence.put(page_payload(str(n), f"<p>Page number {n}.</p>"))
    confluence.put(page_payload("99", "<p>POISON content.</p>"))
    embedder.poison.add("POISON")

    reports = env(DAY_1)

    assert reports["load"].counts["pages_failed"] == 1
    assert reports["load"].counts["pages_indexed"] == 20
    assert store.failures["99"]["stage"] == "load"


def test_too_many_failures_fails_the_stage(env, confluence):
    confluence.put(page_payload("1", "<p>ok</p>"))
    confluence.put(page_payload("2", "<p>ok</p>"))
    confluence.broken.add("2")

    with pytest.raises(StageFailedError):
        env(DAY_1)


def test_reconcile_removes_deleted_pages(env, config, confluence, store):
    confluence.put(page_payload("100", SECTIONS))
    confluence.put(page_payload("200", "<p>Doomed.</p>"))
    env(DAY_1)
    del confluence.pages["200"]

    report = reconcile(config, confluence=confluence, store=store, run_started_at=DAY_2)

    assert report.counts["pages_deleted"] == 1
    assert store.pages["200"]["status"] == "deleted"
    assert store.page_chunks("200") == []
    assert store.page_chunks("100")


def test_reconcile_ignores_pages_indexed_during_this_run(env, config, confluence, store):
    confluence.put(page_payload("100", "<p>Brand new.</p>"))
    env(DAY_1)
    confluence.pages.clear()  # search index has not caught up yet

    report = reconcile(config, confluence=confluence, store=store, run_started_at=DAY_1)

    assert report.counts["pages_deleted"] == 0


def test_reconcile_guard_blocks_mass_deletion(env, config, confluence, store):
    for n in range(1, 6):
        confluence.put(page_payload(str(n), f"<p>Page {n}.</p>"))
    env(DAY_1)
    confluence.pages.clear()  # e.g. service account lost access to the space

    with pytest.raises(DeletionGuardError):
        reconcile(config, confluence=confluence, store=store, run_started_at=DAY_2)
    assert store.count_active_pages() == 5

    report = reconcile(
        config, confluence=confluence, store=store, run_started_at=DAY_2, allow_mass_delete=True
    )
    assert report.counts["pages_deleted"] == 5


def test_reconcile_then_reappearing_page_is_reindexed(env, config, confluence, store):
    confluence.put(page_payload("100", "<p>Restored later.</p>"))
    env(DAY_1)
    payload = confluence.pages.pop("100")
    reconcile(config, confluence=confluence, store=store, run_started_at=DAY_2)

    restored = {
        **payload,
        "version": {
            **payload["version"],
            "number": 2,
            "when": (DAY_2 + timedelta(hours=1)).isoformat(),
        },
    }
    confluence.put(restored)
    env(DAY_2 + timedelta(days=1))

    assert store.pages["100"]["status"] == "active"
    assert store.page_chunks("100")


def test_watermark_never_moves_backwards(config, store):
    commit_watermark(config, store=store, run_id="b", run_started_at=DAY_2)
    commit_watermark(config, store=store, run_id="a", run_started_at=DAY_1)
    assert store.load_date == DAY_2


def test_summary_marks_missing_stages_as_failed(config, store):
    metrics, alerter = MagicMock(), MagicMock()
    ok = {"stage": "x", "counts": {"pages_failed": 0}, "seconds": 1.0, "outputs": {}}

    summary = summarise(
        config,
        {"extract": ok, "transform": ok, "load": None, "commit_watermark": None, "reconcile": ok},
        run_id="r1",
        store=store,
        metrics=metrics,
        alerter=alerter,
    )

    assert summary.status == "failed"
    assert summary.failed_stages == ("load", "commit_watermark")
    counts, _ = metrics.publish.call_args.args
    assert counts["RunFailed"] == 1
    assert store.runs[-1]["status"] == "failed"
    alerter.send.assert_not_called()  # the failing task already alerted


def test_summary_warns_on_degraded_success(config, store):
    metrics, alerter = MagicMock(), MagicMock()
    report = {"stage": "x", "counts": {"pages_failed": 2}, "seconds": 1.0, "outputs": {}}

    summary = summarise(
        config,
        {
            name: report
            for name in ("extract", "transform", "load", "commit_watermark", "reconcile")
        },
        run_id="r1",
        store=store,
        metrics=metrics,
        alerter=alerter,
    )

    assert summary.succeeded
    assert alerter.send.call_args.args[0] == "WARNING"
