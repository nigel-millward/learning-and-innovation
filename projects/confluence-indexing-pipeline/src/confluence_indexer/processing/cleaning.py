"""Convert Confluence storage format (XHTML + ``ac:``/``ri:`` elements) to clean text.

The output is lightweight Markdown: headings become ``#`` lines, lists become
``-`` items and code is fenced. Keeping that structure lets the chunker split
on section boundaries and attribute each chunk to its heading path.

Removed: navigation and dynamic macros (TOC, page trees, child listings,
reports), transcluded content (include/excerpt-include, which is indexed on its
source page), media, macro parameters, ADF fallbacks, configured boilerplate
blocks, and blocks repeated within the page.
"""

from __future__ import annotations

import html
import re
import unicodedata
from collections.abc import Iterable

from bs4 import BeautifulSoup, NavigableString, Tag
from bs4.element import Comment, Declaration, Doctype, ProcessingInstruction

# Macros that render navigation, listings or live data rather than authored content.
DROP_MACROS = frozenset(
    {
        "anchor", "attachments", "blog-posts", "change-history", "children",
        "content-report-table", "contentbylabel", "contributors", "contributors-summary",
        "create-from-template", "create-space-button", "excerpt-include", "favpages",
        "gallery", "include", "index", "jira", "jiraissues", "listlabels", "livesearch",
        "multimedia", "navmap", "page-index", "pagetree", "pagetreesearch",
        "popular-labels", "profile", "profile-picture", "recently-updated",
        "recently-updated-dashboard", "related-labels", "roadmap", "space-details",
        "spaces", "status", "tasks-report-macro", "toc", "view-file", "viewfile", "widget",
    }
)  # fmt: skip
CODE_MACROS = frozenset({"code", "noformat"})
DROP_TAGS = frozenset(
    {
        "script", "style", "ac:image", "ac:emoticon", "ac:placeholder", "ac:parameter",
        "ac:adf-fallback", "ri:user", "ri:attachment", "time",
    }
)  # fmt: skip
BLOCK_TAGS = frozenset(
    {
        "p", "div", "section", "article", "blockquote", "ac:layout", "ac:layout-section",
        "ac:layout-cell", "ac:rich-text-body", "ac:adf-content",
    }
)  # fmt: skip
HEADINGS = {f"h{n}": n for n in range(1, 7)}

DEFAULT_BOILERPLATE = (
    r"(?i)(table of )?contents:?",
    r"(?i)on this page:?",
    r"(?i)back to top",
)

_CDATA = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)
_ZERO_WIDTH = re.compile(r"[​‌‍⁠﻿]")
_CODE_PLACEHOLDER = "\x00CODE{}\x00"
_CODE_TOKEN = re.compile(r"\x00CODE(\d+)\x00")
_LIST_LINE = re.compile(r"^\s*(?:-|\d+\.)\s")
_MIN_DEDUPE_CHARS = 40


class StorageFormatCleaner:
    def __init__(self, boilerplate_patterns: Iterable[str] = ()) -> None:
        self._boilerplate = [
            re.compile(p, re.DOTALL) for p in (*DEFAULT_BOILERPLATE, *boilerplate_patterns)
        ]

    def clean(self, storage_xhtml: str, title: str = "") -> str:
        # Unwrap CDATA up front: it carries code and link text, and parsers
        # disagree on how to treat it outside XML.
        source = _CDATA.sub(lambda m: html.escape(m.group(1)), storage_xhtml or "")
        soup = BeautifulSoup(source, "html.parser")
        renderer = _Renderer()
        text = renderer.render_children(soup)
        return self._postprocess(text, renderer.code_blocks, title)

    def _postprocess(self, text: str, code_blocks: list[str], title: str) -> str:
        text = unicodedata.normalize("NFKC", text)
        text = _ZERO_WIDTH.sub("", text)

        kept: list[str] = []
        seen: set[str] = set()
        title_key = title.strip().lower()
        for raw_block in re.split(r"\n\s*\n", text):
            block = _tidy_block(raw_block)
            if not block or self._is_boilerplate(block):
                continue
            is_heading = block.startswith("#")
            key = re.sub(r"\W+", " ", block).strip().lower()
            if not is_heading and len(block) >= _MIN_DEDUPE_CHARS:
                if key in seen:
                    continue
                seen.add(key)
            # Pages often repeat their own title as the first heading.
            if is_heading and not kept and key == re.sub(r"\W+", " ", title_key).strip():
                continue
            kept.append(block)

        result = "\n\n".join(kept)
        return _CODE_TOKEN.sub(lambda m: code_blocks[int(m.group(1))], result)

    def _is_boilerplate(self, block: str) -> bool:
        stripped = block.lstrip("#").strip()
        return any(p.fullmatch(stripped) for p in self._boilerplate)


def _tidy_block(block: str) -> str:
    lines = []
    for line in block.split("\n"):
        line = line.rstrip()
        if not _LIST_LINE.match(line):
            line = line.lstrip()
        indent = len(line) - len(line.lstrip())
        line = line[:indent] + re.sub(r"[ \t]{2,}", " ", line[indent:])
        if line:
            lines.append(line)
    return "\n".join(lines)


class _Renderer:
    def __init__(self) -> None:
        self.code_blocks: list[str] = []
        self._code_text: list[str] = []
        self._list_depth = 0

    def render_children(self, node: Tag) -> str:
        return "".join(self.render(child) for child in node.children)

    def render(self, node: object) -> str:
        if isinstance(node, (Comment, Declaration, Doctype, ProcessingInstruction)):
            return ""
        if isinstance(node, NavigableString):
            return re.sub(r"\s+", " ", str(node).replace("\xa0", " "))
        if not isinstance(node, Tag):
            return ""

        name = node.name
        if name in DROP_TAGS:
            return ""
        if name in ("ac:structured-macro", "ac:macro"):
            return self._macro(node)
        if name == "ac:link":
            return self._link(node)
        if name == "ac:task-list":
            return self._task_list(node)
        if name in HEADINGS:
            text = self._inline(self.render_children(node))
            return f"\n\n{'#' * HEADINGS[name]} {text}\n\n" if text else ""
        if name in ("ul", "ol"):
            return self._list(node, ordered=name == "ol")
        if name == "table":
            return self._table(node)
        if name == "pre":
            return self._code(node.get_text())
        if name == "br":
            return "\n"
        if name == "hr":
            return "\n\n"

        inner = self.render_children(node)
        if name in BLOCK_TAGS:
            return f"\n\n{inner.strip()}\n\n"
        return inner

    def _macro(self, node: Tag) -> str:
        macro = str(node.get("ac:name") or "").lower()
        if macro in DROP_MACROS:
            return ""
        if macro in CODE_MACROS:
            body = node.find("ac:plain-text-body")
            return self._code(body.get_text()) if body else ""
        body = node.find("ac:rich-text-body", recursive=False)
        if body is None:
            return ""  # parameter-only macros carry no authored prose
        title = node.find("ac:parameter", attrs={"ac:name": "title"}, recursive=False)
        heading = f"\n\n{self._inline(title.get_text())}\n\n" if title else ""
        return f"{heading}\n\n{self.render_children(body).strip()}\n\n"

    def _link(self, node: Tag) -> str:
        for body_tag in ("ac:link-body", "ac:plain-text-link-body"):
            body = node.find(body_tag)
            if body and body.get_text(strip=True):
                return self._inline(body.get_text())
        target = node.find(["ri:page", "ri:blog-post", "ri:space"])
        if target:
            return str(target.get("ri:content-title") or target.get("ri:space-key") or "")
        return ""

    def _list(self, node: Tag, *, ordered: bool) -> str:
        self._list_depth += 1
        try:
            items = []
            for index, li in enumerate(node.find_all("li", recursive=False), start=1):
                marker = f"{index}." if ordered else "-"
                own = "".join(
                    self.render(c)
                    for c in li.children
                    if not (isinstance(c, Tag) and c.name in ("ul", "ol"))
                )
                nested = "".join(
                    self.render(c)
                    for c in li.children
                    if isinstance(c, Tag) and c.name in ("ul", "ol")
                )
                text = self._inline(own)
                if text or nested.strip():
                    indent = "  " * (self._list_depth - 1)
                    items.append(f"{indent}{marker} {text}{nested.rstrip()}")
        finally:
            self._list_depth -= 1
        joined = "\n".join(items)
        return f"\n{joined}" if self._list_depth else f"\n\n{joined}\n\n"

    def _task_list(self, node: Tag) -> str:
        items = []
        for task in node.find_all("ac:task", recursive=False):
            status = task.find("ac:task-status")
            body = task.find("ac:task-body")
            done = status is not None and status.get_text(strip=True) == "complete"
            text = self._inline(self.render_children(body)) if body else ""
            if text:
                items.append(f"- [{'x' if done else ' '}] {text}")
        return "\n\n" + "\n".join(items) + "\n\n" if items else ""

    def _table(self, node: Tag) -> str:
        rows = []
        for tr in node.find_all("tr"):
            if tr.find_parent("table") is not node:
                continue  # rows of nested tables are rendered inside their cell
            cells = [
                self._inline(self.render_children(cell))
                for cell in tr.find_all(["th", "td"], recursive=False)
            ]
            if any(cells):
                rows.append(" | ".join(cells))
        return "\n\n" + "\n".join(rows) + "\n\n" if rows else ""

    def _inline(self, text: str) -> str:
        """Collapse to one line (headings, cells, list items); code stays as inline code."""
        text = _CODE_TOKEN.sub(lambda m: f"`{self._code_text[int(m.group(1))]}`", text)
        return re.sub(r"\s+", " ", text).strip()

    def _code(self, text: str) -> str:
        text = text.strip("\n")
        if not text.strip():
            return ""
        self._code_text.append(text)
        self.code_blocks.append(f"```\n{text}\n```")
        return f"\n\n{_CODE_PLACEHOLDER.format(len(self.code_blocks) - 1)}\n\n"
