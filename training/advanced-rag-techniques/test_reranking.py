"""Characterisation tests for reranking.py.

These tests cover only the parts of the module that do not require a running
Chroma/embedding pipeline, a downloaded cross-encoder model, a running Ollama
server, or network access: pure data transformations and the mapping from
specific exceptions to `sys.exit` messages. The rest of the module (PDF
parsing, Chroma, cross-encoder scoring) is exercised by running the script
manually per README.md, not by this suite.
"""

import httpx
import numpy as np
import ollama
import pytest

import reranking


def test_deduplicate_documents_flattens_and_removes_duplicates_across_queries() -> None:
    documents_per_query = [["a", "b"], ["b", "c"]]

    unique_documents = reranking.deduplicate_documents(documents_per_query)

    assert set(unique_documents) == {"a", "b", "c"}
    assert len(unique_documents) == 3


def test_select_top_reranked_documents_orders_by_score_descending() -> None:
    documents = ["low", "high", "medium"]
    scores = np.array([0.1, 0.9, 0.5])

    top_documents = reranking.select_top_reranked_documents(documents, scores, top_n=2)

    assert top_documents == ["high", "medium"]


def test_print_new_ordering_applies_start_index(capsys) -> None:
    scores = np.array([0.1, 0.9, 0.5])

    reranking.print_new_ordering(scores, start_index=1)

    printed_lines = capsys.readouterr().out.splitlines()
    assert printed_lines == ["New Ordering:", "2", "3", "1"]


def test_generate_answer_from_context_returns_llm_output_on_success(monkeypatch) -> None:
    monkeypatch.setattr(
        reranking,
        "generate_answer_from_context",
        lambda query, context: ["line one", "line two"],
    )

    answer = reranking.generate_answer_from_context_or_exit("a query", "some context")

    assert answer == ["line one", "line two"]


@pytest.mark.parametrize(
    ("raised_exception", "expected_message_fragment"),
    [
        (ConnectionError(), "could not connect to Ollama"),
        (httpx.ConnectError("boom"), "could not connect to Ollama"),
        (httpx.TimeoutException("boom"), "did not respond within"),
    ],
)
def test_generate_answer_from_context_exits_with_clear_message_on_connection_failure(
    monkeypatch, raised_exception, expected_message_fragment
) -> None:
    def raise_exception(query: str, context: str) -> list[str]:
        raise raised_exception

    monkeypatch.setattr(reranking, "generate_answer_from_context", raise_exception)

    with pytest.raises(SystemExit, match=expected_message_fragment):
        reranking.generate_answer_from_context_or_exit("a query", "some context")


def test_generate_answer_from_context_exits_with_clear_message_on_ollama_response_error(
    monkeypatch,
) -> None:
    def raise_response_error(query: str, context: str) -> list[str]:
        raise ollama.ResponseError(error="model not found", status_code=404)

    monkeypatch.setattr(reranking, "generate_answer_from_context", raise_response_error)

    with pytest.raises(SystemExit, match="Ollama returned 404"):
        reranking.generate_answer_from_context_or_exit("a query", "some context")
