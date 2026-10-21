"""Characterisation tests for reranking.py.

These tests cover only the parts of the module that do not require a running
Chroma/embedding pipeline, a downloaded cross-encoder model, or network
access: pure data transformations and the OpenAI response handling. The rest
of the module (PDF parsing, Chroma, cross-encoder scoring) is exercised by
running the script manually per README.md, not by this suite.
"""

import numpy as np
import pytest
from openai.types.chat import ChatCompletion

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


def test_generate_answer_from_context_returns_lines_on_success(monkeypatch) -> None:
    def fake_create(*, model: str, messages: list) -> ChatCompletion:
        return ChatCompletion.model_construct(
            choices=[
                type(
                    "Choice",
                    (),
                    {"message": type("Message", (), {"content": "line one\nline two"})()},
                )()
            ]
        )

    class FakeClient:
        class chat:
            class completions:
                create = staticmethod(fake_create)

    answer = reranking.generate_answer_from_context(FakeClient(), "a query", "some context")

    assert answer == ["line one", "line two"]


def test_generate_answer_from_context_raises_on_missing_content() -> None:
    def fake_create(*, model: str, messages: list) -> ChatCompletion:
        return ChatCompletion.model_construct(
            choices=[type("Choice", (), {"message": type("Message", (), {"content": None})()})()]
        )

    class FakeClient:
        class chat:
            class completions:
                create = staticmethod(fake_create)

    with pytest.raises(ValueError, match="returned no content"):
        reranking.generate_answer_from_context(FakeClient(), "a query", "some context")
