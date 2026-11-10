"""Token-aware, structure-aware chunking of cleaned page text."""

from __future__ import annotations

import bisect
import re

import tiktoken
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

from ..config import ChunkingConfig
from ..models import Chunk, PageMetadata

_HEADING = re.compile(r"^(#{1,6}) (.+)$", re.MULTILINE)


class Chunker:
    """Split cleaned Markdown into overlapping chunks of roughly fixed token size.

    The recursive splitter prefers heading, then paragraph, then line, then
    word boundaries, so chunks follow the page's own structure wherever the
    size budget allows. Each chunk is prefixed with a short contextual header
    (title, space, section path) before embedding, which markedly improves
    retrieval for chunks that never mention the page's subject by name.
    """

    def __init__(self, config: ChunkingConfig) -> None:
        self._encoding = tiktoken.get_encoding(config.encoding_name)
        self._splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name=config.encoding_name,
            chunk_size=config.chunk_size_tokens,
            chunk_overlap=config.chunk_overlap_tokens,
            separators=RecursiveCharacterTextSplitter.get_separators_for_language(
                Language.MARKDOWN
            ),
            is_separator_regex=True,
            keep_separator="start",
            add_start_index=True,
        )

    def chunk(self, page: PageMetadata, text: str) -> list[Chunk]:
        if not text.strip():
            return []
        headings = _heading_positions(text)
        offsets = [pos for pos, _, _ in headings]
        chunks: list[Chunk] = []
        for document in self._splitter.create_documents([text]):
            body = document.page_content.strip()
            if not body:
                continue
            section = _section_at(headings, offsets, document.metadata.get("start_index", 0))
            embedding_text = _contextual_header(page, section) + body
            chunks.append(
                Chunk(
                    page_id=page.page_id,
                    chunk_index=len(chunks),
                    text=body,
                    embedding_text=embedding_text,
                    token_count=len(self._encoding.encode(embedding_text, disallowed_special=())),
                    section=section,
                )
            )
        return chunks


def _heading_positions(text: str) -> list[tuple[int, int, str]]:
    return [(m.start(), len(m.group(1)), m.group(2).strip()) for m in _HEADING.finditer(text)]


def _section_at(
    headings: list[tuple[int, int, str]], offsets: list[int], position: int
) -> tuple[str, ...]:
    """Heading path in force at ``position`` (a chunk starting on a heading belongs to it)."""
    stack: list[tuple[int, str]] = []
    for _, level, title in headings[: bisect.bisect_right(offsets, position)]:
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
    return tuple(title for _, title in stack)


def _contextual_header(page: PageMetadata, section: tuple[str, ...]) -> str:
    lines = [f"Title: {page.title}"]
    if page.space_name or page.space_key:
        lines.append(f"Space: {page.space_name or page.space_key}")
    if page.ancestors:
        lines.append(f"Path: {' > '.join(page.ancestors)}")
    if section:
        lines.append(f"Section: {' > '.join(section)}")
    return "\n".join(lines) + "\n\n"
