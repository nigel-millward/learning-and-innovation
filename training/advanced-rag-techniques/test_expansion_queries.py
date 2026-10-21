"""Characterisation tests for expansion_queries.py.

These tests cover only the parts of the module that do not require a running
Ollama server, a downloaded embedding model, or network access: pure
list/set composition, printing, and the mapping from specific exceptions to
`sys.exit` messages. The rest of the module (PDF parsing, Chroma, UMAP,
plotting) is exercised by running the script manually per README.md, not by
this suite.
"""

import httpx
import ollama
import pytest

import expansion_queries


def test_build_joint_query_prepends_original_query_to_related_queries() -> None:
    joint_query = expansion_queries.build_joint_query(
        "What drove revenue growth?", ["What markets grew?", "What products grew?"]
    )

    assert joint_query == [
        "What drove revenue growth?",
        "What markets grew?",
        "What products grew?",
    ]


def test_build_joint_query_with_no_related_queries_returns_just_the_original() -> None:
    assert expansion_queries.build_joint_query("original", []) == ["original"]


def test_deduplicate_documents_collects_unique_documents_across_queries() -> None:
    unique_documents = expansion_queries.deduplicate_documents(
        [["doc-a", "doc-b"], ["doc-b", "doc-c"]]
    )

    assert unique_documents == {"doc-a", "doc-b", "doc-c"}


def test_deduplicate_documents_with_no_documents_returns_empty_set() -> None:
    assert expansion_queries.deduplicate_documents([]) == set()


def test_flatten_per_query_embeddings_flattens_nested_lists() -> None:
    flattened = expansion_queries.flatten_per_query_embeddings([[1, 2], [3], []])

    assert flattened == [1, 2, 3]


def test_print_retrieved_documents_per_query_prints_each_query_and_its_documents(
    capsys,
) -> None:
    expansion_queries.print_retrieved_documents_per_query(
        ["query one", "query two"], [["doc-a"], ["doc-b", "doc-c"]]
    )

    printed_output = capsys.readouterr().out
    assert "Query: query one" in printed_output
    assert "Query: query two" in printed_output
    assert "doc-a" in printed_output
    assert "doc-b" in printed_output
    assert "doc-c" in printed_output


def test_generate_multi_query_returns_llm_output_on_success(monkeypatch) -> None:
    monkeypatch.setattr(expansion_queries, "generate_multi_query", lambda query: ["q1", "q2"])

    assert expansion_queries.generate_multi_query_or_exit("a question") == ["q1", "q2"]


@pytest.mark.parametrize(
    ("raised_exception", "expected_message_fragment"),
    [
        (ConnectionError(), "could not connect to Ollama"),
        (httpx.ConnectError("boom"), "could not connect to Ollama"),
        (httpx.TimeoutException("boom"), "did not respond within"),
    ],
)
def test_generate_multi_query_exits_with_clear_message_on_connection_failure(
    monkeypatch, raised_exception, expected_message_fragment
) -> None:
    def raise_exception(query: str) -> list[str]:
        raise raised_exception

    monkeypatch.setattr(expansion_queries, "generate_multi_query", raise_exception)

    with pytest.raises(SystemExit, match=expected_message_fragment):
        expansion_queries.generate_multi_query_or_exit("a question")


def test_generate_multi_query_exits_with_clear_message_on_ollama_response_error(
    monkeypatch,
) -> None:
    def raise_response_error(query: str) -> list[str]:
        raise ollama.ResponseError(error="model not found", status_code=404)

    monkeypatch.setattr(expansion_queries, "generate_multi_query", raise_response_error)

    with pytest.raises(SystemExit, match="Ollama returned 404"):
        expansion_queries.generate_multi_query_or_exit("a question")
