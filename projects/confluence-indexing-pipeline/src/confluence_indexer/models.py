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
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PageMetadata:
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

        Expects ``expand=version,space,ancestors,metadata.labels``.
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
        data = asdict(self)
        data["last_modified"] = self.last_modified.isoformat()
        data["labels"] = list(self.labels)
        data["ancestors"] = list(self.ancestors)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PageMetadata:
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
    page_id: str
    chunk_index: int
    text: str  # chunk body, as shown to a user or an LLM
    embedding_text: str  # contextual header + body; this is what gets embedded
    token_count: int  # tokens in embedding_text
    section: tuple[str, ...]  # heading path within the page
    content_hash: str = field(init=False)

    def __post_init__(self) -> None:
        # The hash covers exactly what is embedded, so any change that would
        # change the vector (body, title, breadcrumb) changes the hash.
        object.__setattr__(self, "content_hash", sha256_hex(self.embedding_text))

    @property
    def chunk_id(self) -> str:
        return f"{self.page_id}:{self.chunk_index:05d}"

    def to_dict(self) -> dict[str, Any]:
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
        return cls(**{**data, "section": tuple(data["section"])})


@dataclass(frozen=True)
class PageDocument:
    """A cleaned, chunked page ready for embedding and loading."""

    metadata: PageMetadata
    raw_uri: str
    chunks: tuple[Chunk, ...]

    @property
    def page_id(self) -> str:
        return self.metadata.page_id

    @property
    def content_hash(self) -> str:
        """Fingerprint of everything that would be written for this page.

        Equal hashes mean the stored rows are already correct, so the page can
        be skipped without touching the embedding API or the vector index.
        """
        meta = self.metadata.to_dict()
        # Version and timestamps change on every save, even when the text does not.
        for volatile in ("version", "last_modified", "last_modified_by"):
            meta.pop(volatile)
        payload = {"meta": meta, "chunks": [c.content_hash for c in self.chunks]}
        return sha256_hex(json.dumps(payload, sort_keys=True))

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "raw_uri": self.raw_uri,
            "chunks": [c.to_dict() for c in self.chunks],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PageDocument:
        return cls(
            metadata=PageMetadata.from_dict(data["metadata"]),
            raw_uri=data["raw_uri"],
            chunks=tuple(Chunk.from_dict(c) for c in data["chunks"]),
        )


@dataclass(frozen=True)
class IndexedPage:
    """What the vector store currently holds for a page."""

    page_id: str
    version: int
    content_hash: str
    embedding_version: str
