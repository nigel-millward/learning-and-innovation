"""Tests for token-based chunking of cleaned page text."""

from datetime import UTC, datetime
from itertools import pairwise

import tiktoken

from confluence_indexer.config import ChunkingConfig
from confluence_indexer.models import PageMetadata
from confluence_indexer.processing.chunking import Chunker

PAGE = PageMetadata(
    page_id="42",
    space_key="ENG",
    space_name="Engineering",
    title="Release process",
    url="https://example/wiki/42",
    version=3,
    last_modified=datetime(2026, 11, 1, tzinfo=UTC),
    last_modified_by="Ada",
    labels=("release",),
    ancestors=("Engineering Home", "Processes"),
)

DOC = "\n\n".join(
    f"## Stage {n}\n\n"
    + "\n\n".join(
        f"Step {n}.{p}: " + "verify the artefact checksum and promote it. " * 6 for p in range(4)
    )
    for n in range(1, 5)
)

encoding = tiktoken.get_encoding("cl100k_base")


def make(size=150, overlap=20):
    return Chunker(ChunkingConfig(chunk_size_tokens=size, chunk_overlap_tokens=overlap))


def test_chunks_respect_token_budget():
    chunks = make().chunk(PAGE, DOC)
    assert len(chunks) > 3
    for chunk in chunks:
        assert len(encoding.encode(chunk.text)) <= 150


def test_chunks_overlap():
    chunks = make().chunk(PAGE, DOC)
    overlapping = sum(1 for a, b in pairwise(chunks) if a.text[-40:].split()[-1] in b.text)
    assert overlapping > 0


def test_chunks_carry_section_path_and_contextual_header():
    chunks = make().chunk(PAGE, DOC)
    last = chunks[-1]
    assert last.section == ("Stage 4",)
    assert last.embedding_text.startswith(
        "Title: Release process\nSpace: Engineering\nPath: Engineering Home > Processes\n"
        "Section: Stage 4\n\n"
    )
    assert last.embedding_text.endswith(last.text)
    assert last.token_count == len(encoding.encode(last.embedding_text))


def test_nested_headings_build_a_path():
    doc = "# Guide\n\nIntro.\n\n## Install\n\nRun it.\n\n### macOS\n\nUse brew.\n\n## Usage\n\nGo."
    chunks = make(size=8, overlap=0).chunk(PAGE, doc)
    sections = {c.text: c.section for c in chunks}
    assert sections["### macOS\n\nUse brew."] == ("Guide", "Install", "macOS")
    assert sections["## Usage\n\nGo."] == ("Guide", "Usage")


def test_chunking_is_deterministic_with_stable_ids_and_hashes():
    first = make().chunk(PAGE, DOC)
    second = make().chunk(PAGE, DOC)
    assert [(c.chunk_id, c.content_hash) for c in first] == [
        (c.chunk_id, c.content_hash) for c in second
    ]
    assert first[0].chunk_id == "42:00000"


def test_empty_text_has_no_chunks():
    assert make().chunk(PAGE, "  \n ") == []
