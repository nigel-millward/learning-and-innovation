"""Characterisation tests for expansion_answer.py.

These tests cover only the parts of the module that do not require a running
Ollama server, a downloaded embedding model, or network access: pure string
composition and the mapping from specific exceptions to `sys.exit` messages.
The rest of the module (PDF parsing, Chroma, UMAP, plotting) is exercised by
running the script manually per README.md, not by this suite.
"""

import httpx
import ollama
import pytest

import expansion_answer


def test_build_hyde_query_joins_original_query_and_hypothetical_answer() -> None:
    joint_query = expansion_answer.build_hyde_query(
        "What was the total profit?", "Profit was $10bn, up from $8bn."
    )

    assert joint_query == "What was the total profit? Profit was $10bn, up from $8bn."


def test_generate_hypothetical_answer_returns_llm_output_on_success(monkeypatch) -> None:
    monkeypatch.setattr(expansion_answer, "augment_query_generated", lambda query: "an answer")

    assert expansion_answer.generate_hypothetical_answer_or_exit("a question") == "an answer"


@pytest.mark.parametrize(
    ("raised_exception", "expected_message_fragment"),
    [
        (ConnectionError(), "could not connect to Ollama"),
        (httpx.ConnectError("boom"), "could not connect to Ollama"),
        (httpx.TimeoutException("boom"), "did not respond within"),
    ],
)
def test_generate_hypothetical_answer_exits_with_clear_message_on_connection_failure(
    monkeypatch, raised_exception, expected_message_fragment
) -> None:
    def raise_exception(query: str) -> str:
        raise raised_exception

    monkeypatch.setattr(expansion_answer, "augment_query_generated", raise_exception)

    with pytest.raises(SystemExit, match=expected_message_fragment):
        expansion_answer.generate_hypothetical_answer_or_exit("a question")


def test_generate_hypothetical_answer_exits_with_clear_message_on_ollama_response_error(
    monkeypatch,
) -> None:
    def raise_response_error(query: str) -> str:
        raise ollama.ResponseError(error="model not found", status_code=404)

    monkeypatch.setattr(expansion_answer, "augment_query_generated", raise_response_error)

    with pytest.raises(SystemExit, match="Ollama returned 404"):
        expansion_answer.generate_hypothetical_answer_or_exit("a question")
