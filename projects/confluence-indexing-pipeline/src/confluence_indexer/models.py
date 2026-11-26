"""Data passed between pipeline stages.

Every model round-trips through plain JSON (``to_dict``/``from_dict``) because
stages run as separate Airflow tasks, possibly on different workers, and hand
data over via the S3 landing zone rather than in memory.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


def sha256_hex(text: str) -> str:
    """Return the SHA-256 hex digest of the UTF-8 encoding of a string.

    Args:
        text: Text to hash.

    Returns:
        The 64-character lowercase hex digest.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PageMetadata:
    """Descriptive fields of a Confluence page, everything except its body.

    Attributes:
        page_id: Confluence content ID.
        space_key: Key of the space the page belongs to.
        space_name: Display name of that space.
        title: Page title.
        url: Absolute web URL of the page, or empty if the payload has no link.
        version: Confluence version number; increases on every save.
        last_modified: Time of the latest version.
        last_modified_by: Display name of the latest version's author, if known.
        labels: Label names, sorted.
        ancestors: Titles of the parent pages, root first.
    """

    page_id: str
    space_key: str
    space_name: str
    title: str
    url: str
    version: int
    last_modified: datetime
    last_modified_by: str | None
    labels: tuple[str, ...]
    ancestors: tuple[str, ...]  # titles, root first

    @classmethod
    def from_api(cls, payload: dict[str, Any], base_url: str) -> PageMetadata:
        """Build from a Confluence content payload.

        Expects ``expand=version,space,ancestors,metadata.labels``. Missing
        optional fields fall back to empty values.

        Args:
            payload: Content JSON as returned by the Confluence REST API.
            base_url: Site base URL, used when the payload has no ``_links.base``.

        Returns:
            The page metadata.

        Raises:
            KeyError: If the payload has no ``id`` or no ``version.when``.
        """
        version = payload.get("version") or {}
        space = payload.get("space") or {}
        links = payload.get("_links") or {}
        url_base = links.get("base") or base_url
        labels = (payload.get("metadata") or {}).get("labels", {}).get("results", [])
        return cls(
            page_id=str(payload["id"]),
            space_key=space.get("key", ""),
            space_name=space.get("name", ""),
            title=payload.get("title", ""),
            url=f"{url_base}{links['webui']}" if links.get("webui") else "",
            version=int(version.get("number", 0)),
            last_modified=datetime.fromisoformat(version["when"]),
            last_modified_by=(version.get("by") or {}).get("displayName"),
            labels=tuple(sorted(label["name"] for label in labels)),
            ancestors=tuple(a.get("title", "") for a in payload.get("ancestors") or []),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serialisable dict.

        Returns:
            The fields, with the timestamp as ISO 8601 and tuples as lists.
        """
        data = asdict(self)
        data["last_modified"] = self.last_modified.isoformat()
        data["labels"] = list(self.labels)
        data["ancestors"] = list(self.ancestors)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PageMetadata:
        """Rebuild from the output of ``to_dict``.

        Args:
            data: Dict produced by ``to_dict``.

        Returns:
            The page metadata.
        """
        return cls(
            **{
                **data,
                "last_modified": datetime.fromisoformat(data["last_modified"]),
                "labels": tuple(data["labels"]),
                "ancestors": tuple(data["ancestors"]),
            }
        )


@dataclass(frozen=True)
class Chunk:
    """One piece of a page, sized for embedding.

    Attributes:
        page_id: ID of the page the chunk came from.
        chunk_index: Position of the chunk within the page, from 0.
        text: Chunk body, as shown to a user or an LLM.
        embedding_text: Contextual header plus body; this is what gets embedded.
        token_count: Number of tokens in ``embedding_text``.
        section: Heading path within the page.
        content_hash: SHA-256 of ``embedding_text``, computed on creation.
    """

    page_id: str
    chunk_index: int
    text: str  # chunk body, as shown to a user or an LLM
    embedding_text: str  # contextual header + body; this is what gets embedded
    token_count: int  # tokens in embedding_text
    section: tuple[str, ...]  # heading path within the page
    content_hash: str = field(init=False)

    def __post_init__(self) -> None:
        """Compute ``content_hash`` from ``embedding_text``."""
        # The hash covers exactly what is embedded, so any change that would
        # change the vector (body, title, breadcrumb) changes the hash.
        object.__setattr__(self, "content_hash", sha256_hex(self.embedding_text))

    @property
    def chunk_id(self) -> str:
        """Stable ID of the chunk: page ID and zero-padded chunk index."""
        return f"{self.page_id}:{self.chunk_index:05d}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serialisable dict.

        ``content_hash`` is left out because it is recomputed on load.

        Returns:
            The constructor fields, with ``section`` as a list.
        """
        return {
            "page_id": self.page_id,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "embedding_text": self.embedding_text,
            "token_count": self.token_count,
            "section": list(self.section),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Chunk:
        """Rebuild from the output of ``to_dict``.

        Args:
            data: Dict produced by ``to_dict``.

        Returns:
            The chunk, with its ``content_hash`` recomputed.
        """
        return cls(**{**data, "section": tuple(data["section"])})


@dataclass(frozen=True)
class PageDocument:
    """A cleaned, chunked page ready for embedding and loading.

    Attributes:
        metadata: Descriptive fields of the page.
        raw_uri: S3 URI of the raw page payload in the landing zone.
        chunks: The page's chunks, in order.
    """

    metadata: PageMetadata
    raw_uri: str
    chunks: tuple[Chunk, ...]

    @property
    def page_id(self) -> str:
        """ID of the page, taken from its metadata."""
        return self.metadata.page_id

    @property
    def content_hash(self) -> str:
        """Fingerprint of everything that would be written for this page.

        Equal hashes mean the stored rows are already correct, so the page can
        be skipped without touching the embedding API or the vector index.
        Version and modification fields are left out because they change on
        every save, even when the text does not.
        """
        meta = self.metadata.to_dict()
        # Version and timestamps change on every save, even when the text does not.
        for volatile in ("version", "last_modified", "last_modified_by"):
            meta.pop(volatile)
        payload = {"meta": meta, "chunks": [c.content_hash for c in self.chunks]}
        return sha256_hex(json.dumps(payload, sort_keys=True))

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serialisable dict.

        Returns:
            The metadata, raw URI and chunks, each converted with ``to_dict``.
        """
        return {
            "metadata": self.metadata.to_dict(),
            "raw_uri": self.raw_uri,
            "chunks": [c.to_dict() for c in self.chunks],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PageDocument:
        """Rebuild from the output of ``to_dict``.

        Args:
            data: Dict produced by ``to_dict``.

        Returns:
            The page document.
        """
        return cls(
            metadata=PageMetadata.from_dict(data["metadata"]),
            raw_uri=data["raw_uri"],
            chunks=tuple(Chunk.from_dict(c) for c in data["chunks"]),
        )


@dataclass(frozen=True)
class IndexedPage:
    """What the vector store currently holds for a page.

    Attributes:
        page_id: Confluence content ID.
        version: Confluence version number that was indexed.
        content_hash: ``PageDocument.content_hash`` at the time it was indexed.
        embedding_version: Embedding space the page's chunks were embedded in.
    """

    page_id: str
    version: int
    content_hash: str
    embedding_version: str
