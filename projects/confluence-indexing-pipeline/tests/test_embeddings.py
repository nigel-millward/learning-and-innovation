from types import SimpleNamespace

import httpx
import ollama
import pytest

from confluence_indexer.integrations.embeddings import EmbeddingError, OllamaEmbeddingProvider


class FakeOllamaClient:
    def __init__(self, dims=4, error=None):
        self.dims = dims
        self.error = error
        self.calls = []

    def embed(self, model, input, truncate):
        self.calls.append((model, list(input), truncate))
        if self.error:
            raise self.error
        return SimpleNamespace(embeddings=[[float(len(t))] * self.dims for t in input])


def provider(client, dims=4, batch_size=2):
    return OllamaEmbeddingProvider(
        client, "nomic-embed-text", dims, batch_size, "http://localhost:11434"
    )


def test_batches_preserve_order_and_never_truncate():
    client = FakeOllamaClient()
    vectors = provider(client).embed(["a", "bb", "ccc"])
    assert [v[0] for v in vectors] == [1.0, 2.0, 3.0]
    assert [len(call[1]) for call in client.calls] == [2, 1]
    assert all(call[2] is False for call in client.calls)


def test_dimension_mismatch_explains_the_fix():
    with pytest.raises(EmbeddingError, match="EMBEDDING_DIMENSIONS"):
        provider(FakeOllamaClient(dims=768), dims=1536).embed(["a"])


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (httpx.ConnectError("refused"), "Is `ollama serve` running"),
        (httpx.ReadTimeout("slow"), "timed out"),
        (ollama.ResponseError("model not found", 404), "ollama pull nomic-embed-text"),
    ],
)
def test_ollama_errors_are_actionable(error, message):
    with pytest.raises(EmbeddingError, match=message):
        provider(FakeOllamaClient(error=error)).embed(["a"])
