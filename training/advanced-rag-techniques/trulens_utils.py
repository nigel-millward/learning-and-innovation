"""Shared TruLens RAG Triad evaluation for the course scripts.

The RAG Triad scores one RAG pass (query -> retrieved context -> answer) on
three legs, each between 0 and 1 (closer to 1 is better):

- Context Relevance: is each retrieved document relevant to the query?
- Groundedness: is each sentence of the answer supported by the context?
- Answer Relevance: does the answer address the query?

This module only configures TruLens; TruLens does the scoring, drops judge
replies it cannot parse, and stores every run in `trulens.sqlite`, so the
leaderboard compares runs and versions. A script marks its own retrieve and
answer steps with TruLens's `@instrument`, because what counts as "the
context" is part of the technique being measured; reranking.py is the
example.

The judge is a local Ollama model reached through TruLens's LiteLLM provider.
It is the `llama3.2-judge` variant built from `modelfiles/`, which raises
Ollama's 4096-token default context (it would silently truncate a long
prompt) and caps the length of each verdict.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Callable

import httpx
import numpy as np
import ollama
import pandas as pd
from trulens.apps.app import TruApp
from trulens.core import Metric, Selector, TruSession
from trulens.core.feedback.feedback import GroundednessConfigs
from trulens.core.otel.recording import Recording
from trulens.feedback import UNPARSABLE_SCORE
from trulens.providers.litellm import LiteLLM

EVALUATION_MODEL: str = "llama3.2-judge"
OLLAMA_BASE_URL: str = "http://localhost:11434"
DATABASE_PATH: Path = Path(__file__).resolve().parent / "trulens.sqlite"
# Scoring runs one judge call per context document and per answer sentence.
FEEDBACK_TIMEOUT_SECONDS: int = 900
# TruLens normally asks the judge to drop "trivial" sentences before scoring
# groundedness. A 3B model also drops unsupported claims that way, which
# inflates the score, so every sentence of the answer is scored instead.
GROUNDEDNESS_CONFIGS: GroundednessConfigs = GroundednessConfigs(
    use_sent_tokenize=True, filter_trivial_statements=False
)
RAG_TRIAD_METRIC_NAMES: list[str] = ["Context Relevance", "Groundedness", "Answer Relevance"]


def quiet_trulens_logging() -> None:
    """Hides TruLens and LiteLLM warnings so the report stays readable.

    Call this from a script's `main()`; it changes logging for the whole
    process. Errors are still shown.
    """
    for logger_name in ("trulens", "LiteLLM"):
        logging.getLogger(logger_name).setLevel(logging.ERROR)


def check_model_available_or_exit(model: str, base_url: str) -> None:
    """Exits with a clear message unless Ollama is serving `model`.

    TruLens retries a judge call that fails and records the error against
    the score, so a missing judge model would otherwise surface as a long
    wait and blank scores rather than a clear error.

    Args:
        model: The Ollama model name to check.
        base_url: The Ollama server URL.
    """
    try:
        ollama.Client(host=base_url).show(model)
    except (ConnectionError, httpx.ConnectError):
        sys.exit(f"Error: could not connect to Ollama at {base_url}. Is `ollama serve` running?")
    except ollama.ResponseError as exc:
        sys.exit(
            f"Error: Ollama returned {exc.status_code} for judge model {model!r}. "
            f"Build it with `ollama create {model} -f modelfiles/{model}.Modelfile`."
        )


def build_rag_triad_metrics(model: str, base_url: str) -> list[Metric]:
    """Defines the three RAG Triad metrics, judged by a local Ollama model.

    Args:
        model: The Ollama model name to judge with.
        base_url: The Ollama server URL.

    Returns:
        TruLens metrics for context relevance, groundedness and answer
        relevance.
    """
    provider: LiteLLM = LiteLLM(model_engine=f"ollama_chat/{model}", api_base=base_url)
    return [
        Metric(
            implementation=provider.context_relevance_with_cot_reasons,
            name="Context Relevance",
            selectors={
                "question": Selector.select_record_input(),
                "context": Selector.select_context(collect_list=False),
            },
            agg=np.mean,
        ),
        Metric(
            implementation=provider.groundedness_measure_with_cot_reasons,
            name="Groundedness",
            selectors={
                "source": Selector.select_context(collect_list=True),
                "statement": Selector.select_record_output(),
            },
            groundedness_configs=GROUNDEDNESS_CONFIGS,
        ),
        Metric(
            implementation=provider.relevance_with_cot_reasons,
            name="Answer Relevance",
            selectors={
                "prompt": Selector.select_record_input(),
                "response": Selector.select_record_output(),
            },
        ),
    ]


def build_rag_triad_recorder(
    app: Any,
    main_method: Callable[[str], str],
    app_name: str,
    app_version: str,
    model: str = EVALUATION_MODEL,
    base_url: str = OLLAMA_BASE_URL,
) -> TruApp:
    """Wraps an instrumented RAG app so each recorded query is scored.

    Use it as `with recorder as recording: app.query(...)`, then pass
    `recording` to `print_rag_triad_report`.

    Args:
        app: An object whose retrieve step is marked with
            `@instrument(span_type=SpanAttributes.SpanType.RETRIEVAL, ...)`.
        main_method: The app's method that takes the query and returns the
            answer.
        app_name: The technique's name on the leaderboard.
        app_version: Bump this when the technique's settings change, so the
            leaderboard compares the versions.
        model: The Ollama model name to judge with.
        base_url: The Ollama server URL.

    Returns:
        The TruLens recorder.
    """
    check_model_available_or_exit(model, base_url)
    TruSession(database_url=f"sqlite:///{DATABASE_PATH}")
    return TruApp(
        app,
        app_name=app_name,
        app_version=app_version,
        feedbacks=build_rag_triad_metrics(model, base_url),
        main_method=main_method,
    )


def select_rag_triad_scores(scores: pd.DataFrame) -> pd.DataFrame:
    """Keeps the RAG Triad columns, with unusable scores shown as NaN.

    Args:
        scores: A TruLens feedback-results or leaderboard DataFrame.

    Returns:
        The three RAG Triad columns, rounded to two decimals. A metric with
        no usable verdict (missing, or TruLens's unparsable sentinel) is NaN.
    """
    triad: pd.DataFrame = scores.reindex(columns=RAG_TRIAD_METRIC_NAMES)
    return triad.replace(UNPARSABLE_SCORE, np.nan).round(2)


def print_rag_triad_report(recording: Recording, model: str = EVALUATION_MODEL) -> pd.DataFrame:
    """Waits for this run's RAG Triad scores, then prints them and the leaderboard.

    Args:
        recording: The recording from `with recorder as recording:`.
        model: The judge model's name, for the report heading.

    Returns:
        This run's scores.
    """
    run_scores: pd.DataFrame = select_rag_triad_scores(
        recording.retrieve_feedback_results(timeout=FEEDBACK_TIMEOUT_SECONDS)
    )
    leaderboard: pd.DataFrame = select_rag_triad_scores(TruSession().get_leaderboard())
    title: str = f"RAG Triad report (TruLens, judge: {model})"
    print("")
    print(title)
    print("=" * len(title))
    print(run_scores.T.to_string(header=False))
    print("")
    print(f"Leaderboard: mean per technique over every run in {DATABASE_PATH.name}")
    print(leaderboard.to_string())
    print("")
    print("Scores run from 0 to 1; closer to 1 is better. NaN: the judge gave no usable verdict.")
    return run_scores
