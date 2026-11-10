"""Embedding providers.

``ollama`` runs locally with no API key (``ollama serve`` + ``ollama pull
nomic-embed-text``) and is the default for development. ``openai``,
``azure_openai`` and ``bedrock`` are the hosted options for deployed
environments. All return vectors of exactly ``dimensions`` or raise.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Protocol

from ..config import EmbeddingConfig

log = logging.getLogger(__name__)

Vector = list[float]


class EmbeddingError(RuntimeError):
    pass


class EmbeddingProvider(Protocol):
    dimensions: int

    def embed(self, texts: Sequence[str]) -> list[Vector]:
        """Embed ``texts``, returning one vector per input in the same order."""
        ...


class OllamaEmbeddingProvider:
    """Embeddings from a local (or self-hosted) Ollama server.

    Ollama models have a fixed output size (nomic-embed-text: 768,
    mxbai-embed-large: 1024), so EMBEDDING_DIMENSIONS must match the model.
    Inputs are never silently truncated: an over-long chunk fails loudly and is
    dead-lettered rather than being indexed from a partial embedding.
    """

    def __init__(
        self, client: Any, model: str, dimensions: int, batch_size: int, base_url: str
    ) -> None:
        self._client = client
        self._model = model
        self.dimensions = dimensions
        self._batch_size = batch_size
        self._base_url = base_url

    def embed(self, texts: Sequence[str]) -> list[Vector]:
        import httpx
        import ollama

        vectors: list[Vector] = []
        for start in range(0, len(texts), self._batch_size):
            batch = list(texts[start : start + self._batch_size])
            try:
                response = self._client.embed(model=self._model, input=batch, truncate=False)
            except (ConnectionError, httpx.ConnectError) as exc:
                raise EmbeddingError(
                    f"Could not connect to Ollama at {self._base_url}. Is `ollama serve` running?"
                ) from exc
            except httpx.TimeoutException as exc:
                raise EmbeddingError(f"Ollama at {self._base_url} timed out") from exc
            except ollama.ResponseError as exc:
                hint = f" (run `ollama pull {self._model}`)" if exc.status_code == 404 else ""
                raise EmbeddingError(
                    f"Ollama returned {exc.status_code}: {exc.error}{hint}"
                ) from exc
            vectors.extend(list(vector) for vector in response.embeddings)
        return _validated(vectors, len(texts), self.dimensions)


class OpenAIEmbeddingProvider:
    """OpenAI or Azure OpenAI, depending on the client passed in.

    ``text-embedding-3-*`` models accept a ``dimensions`` argument that returns
    a shortened, still-normalised vector. 1536 dimensions keeps the column
    within pgvector's 2000-dimension limit for HNSW on ``vector``.
    """

    def __init__(self, client: Any, model: str, dimensions: int, batch_size: int) -> None:
        self._client = client
        self._model = model
        self.dimensions = dimensions
        self._batch_size = batch_size

    def embed(self, texts: Sequence[str]) -> list[Vector]:
        vectors: list[Vector] = []
        for start in range(0, len(texts), self._batch_size):
            batch = list(texts[start : start + self._batch_size])
            response = self._client.embeddings.create(
                model=self._model, input=batch, dimensions=self.dimensions
            )
            # The API does not guarantee response order; ``index`` does.
            ordered = sorted(response.data, key=lambda item: item.index)
            vectors.extend(list(item.embedding) for item in ordered)
        return _validated(vectors, len(texts), self.dimensions)


class BedrockTitanEmbeddingProvider:
    """Amazon Titan Text Embeddings v2, which embeds one text per request."""

    def __init__(self, client: Any, model_id: str, dimensions: int, concurrency: int = 8) -> None:
        if dimensions not in (256, 512, 1024):
            raise EmbeddingError("Titan Text Embeddings v2 supports 256, 512 or 1024 dimensions")
        self._client = client
        self._model_id = model_id
        self.dimensions = dimensions
        self._concurrency = concurrency

    def embed(self, texts: Sequence[str]) -> list[Vector]:
        with ThreadPoolExecutor(max_workers=self._concurrency) as pool:
            vectors = list(pool.map(self._embed_one, texts))
        return _validated(vectors, len(texts), self.dimensions)

    def _embed_one(self, text: str) -> Vector:
        body = json.dumps({"inputText": text, "dimensions": self.dimensions, "normalize": True})
        response = self._client.invoke_model(
            modelId=self._model_id,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        return list(json.loads(response["body"].read())["embedding"])


def build_embedding_provider(config: EmbeddingConfig) -> EmbeddingProvider:
    client: Any
    if config.provider == "ollama":
        import ollama

        client = ollama.Client(host=config.ollama_base_url, timeout=config.timeout_seconds)
        return OllamaEmbeddingProvider(
            client, config.model, config.dimensions, config.batch_size, config.ollama_base_url
        )

    if config.provider == "bedrock":
        import boto3
        from botocore.config import Config

        client = boto3.client(
            "bedrock-runtime",
            region_name=config.aws_region,
            config=Config(retries={"max_attempts": 10, "mode": "adaptive"}),
        )
        return BedrockTitanEmbeddingProvider(client, config.model, config.dimensions)

    import openai

    # The SDK retries 429/5xx with backoff; raise it from the default of 2 for batch work.
    if config.provider == "azure_openai":
        client = openai.AzureOpenAI(
            api_key=config.api_key,
            azure_endpoint=str(config.azure_endpoint),  # validated in EmbeddingConfig
            api_version=config.azure_api_version,
            max_retries=8,
            timeout=config.timeout_seconds,
        )
    else:
        client = openai.OpenAI(
            api_key=config.api_key, max_retries=8, timeout=config.timeout_seconds
        )
    return OpenAIEmbeddingProvider(client, config.model, config.dimensions, config.batch_size)


def _validated(vectors: list[Vector], expected: int, dimensions: int) -> list[Vector]:
    if len(vectors) != expected:
        raise EmbeddingError(f"Expected {expected} embeddings, got {len(vectors)}")
    for vector in vectors:
        if len(vector) != dimensions:
            raise EmbeddingError(
                f"Model returned {len(vector)}-dimension vectors but EMBEDDING_DIMENSIONS is "
                f"{dimensions}; set it to match the model and migrate the schema"
            )
    return vectors
