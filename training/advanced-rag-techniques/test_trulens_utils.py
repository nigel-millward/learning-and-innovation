"""Characterisation tests for trulens_utils.py.

These tests cover only the parts of the module that do not require a running
Ollama server or a TruLens database: the metric definitions, the mapping
from a missing judge model to `sys.exit` messages, and report formatting.
Recording and scoring are exercised by running reranking.py,
expansion_answer.py or expansion_queries.py manually per README.md, not by
this suite.
"""

import re

import httpx
import numpy as np
import ollama
import pandas as pd
import pytest
from trulens.feedback import UNPARSABLE_SCORE

import trulens_utils


def test_build_rag_triad_metrics_defines_the_three_triad_metrics() -> None:
    metrics = trulens_utils.build_rag_triad_metrics("llama3.2-judge", "http://ollama")

    assert [metric.name for metric in metrics] == trulens_utils.RAG_TRIAD_METRIC_NAMES


@pytest.mark.parametrize(
    ("raised_exception", "expected_message_fragment"),
    [
        (ConnectionError(), "could not connect to Ollama"),
        (httpx.ConnectError("boom"), "could not connect to Ollama"),
        (
            ollama.ResponseError(error="model not found", status_code=404),
            "ollama create llama3.2-judge -f modelfiles/llama3.2-judge.Modelfile",
        ),
    ],
)
def test_check_model_available_or_exit_explains_how_to_fix_a_missing_judge(
    monkeypatch, raised_exception, expected_message_fragment
) -> None:
    def raise_exception(self, model: str) -> None:
        raise raised_exception

    monkeypatch.setattr(ollama.Client, "show", raise_exception)

    with pytest.raises(SystemExit, match=expected_message_fragment):
        trulens_utils.check_model_available_or_exit("llama3.2-judge", "http://ollama")


def test_select_rag_triad_scores_keeps_triad_columns_and_blanks_unusable_scores() -> None:
    scores = pd.DataFrame(
        {"Context Relevance": [0.666666], "Groundedness": [UNPARSABLE_SCORE], "latency": [1.5]}
    )

    triad = trulens_utils.select_rag_triad_scores(scores)

    assert list(triad.columns) == trulens_utils.RAG_TRIAD_METRIC_NAMES
    assert triad["Context Relevance"].iloc[0] == 0.67
    assert np.isnan(triad["Groundedness"].iloc[0])
    assert np.isnan(triad["Answer Relevance"].iloc[0])


class FakeRecording:
    """Stands in for a TruLens recording with fixed feedback results."""

    def retrieve_feedback_results(self, timeout: float) -> pd.DataFrame:
        return pd.DataFrame(
            {"Context Relevance": [0.5], "Groundedness": [1.0], "Answer Relevance": [0.25]}
        )


class FakeTruSession:
    """Stands in for the TruLens session, with a fixed leaderboard."""

    def get_leaderboard(self) -> pd.DataFrame:
        return pd.DataFrame(
            {"Context Relevance": [0.4], "Groundedness": [0.9], "Answer Relevance": [0.3]},
            index=pd.Index(["reranking"], name="app_name"),
        )


def test_print_rag_triad_report_prints_run_scores_and_leaderboard(monkeypatch, capsys) -> None:
    monkeypatch.setattr(trulens_utils, "TruSession", FakeTruSession)

    run_scores = trulens_utils.print_rag_triad_report(FakeRecording(), model="judge")

    printed_output = capsys.readouterr().out
    assert "RAG Triad report (TruLens, judge: judge)" in printed_output
    assert re.search(r"Answer Relevance\s+0\.25", printed_output)
    assert "Leaderboard" in printed_output
    assert "reranking" in printed_output
    assert run_scores["Groundedness"].iloc[0] == 1.0
