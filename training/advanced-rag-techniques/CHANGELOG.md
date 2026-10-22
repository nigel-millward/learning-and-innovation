# Changelog — Advanced RAG Techniques

Course-level changes, newest first. Dates are spoken in lectures, never rendered on slides.

## 2026-10-22

**Code**
- `reranking.py` now generates its final answer with a local Ollama `llama3.2` model via LangChain `ChatOllama`, matching `expansion_answer.py` and `expansion_queries.py`. It no longer calls OpenAI, so no `OPENAI_API_KEY` or `.env` file is needed anywhere in the project.
- `build_openai_client()` removed; `generate_answer_from_context()` no longer takes a client argument, and the new `generate_answer_from_context_or_exit()` maps connection, timeout and `ollama.ResponseError` failures to clear `sys.exit` messages.
- `openai` and `python-dotenv` dropped from `requirements.txt`; nothing imports them now.
- `reranking.py` now ends with a RAG Triad report from [TruLens](https://www.trulens.org): context relevance (over the top re-ranked documents), groundedness and answer relevance, each 0 to 1. Scenario B is wrapped in a small `RerankingRag` class whose retrieve and generate steps are marked with TruLens's `@instrument`, and one query is recorded with `TruApp`. The report prints this run's scores plus TruLens's leaderboard over every run stored in `trulens.sqlite` (gitignored). The other scripts are unchanged and still run quickly.
- New shared `trulens_utils.py` defines the three TruLens `Metric`s, builds the recorder and prints the report, so another script can add the RAG Triad with a few lines; `reranking.py` is the example. The judge is TruLens's LiteLLM provider calling a local Ollama model, so no API key is needed. Groundedness scores every sentence of the answer, because `llama3.2` drops unsupported claims when TruLens's trivial-statement filter is on.
- New `modelfiles/llama3.2-judge.Modelfile` builds the judge: `llama3.2` with a 16k-token context (Ollama's 4096-token default silently truncates longer prompts) and replies capped at 512 tokens (forced into JSON, the small model sometimes never stops, which stalled a run for minutes). Build it once with `ollama create llama3.2-judge -f modelfiles/llama3.2-judge.Modelfile`.
- `trulens-core` and `trulens-providers-litellm` added to `requirements.txt`.

## 2026-09-15

**Code**
- Chat model default changed from `gpt-3.5-turbo` to `gpt-5.6-luna` in `expansion_queries.py`, `expansion_answer.py`, `reranking.py`. OpenAI retires `gpt-3.5-turbo-0125` on 2026-10-23. Embeddings are local sentence-transformers and are unaffected.
- README rewritten to describe the course, the script-to-section map, setup and troubleshooting.
- `scikit-learn` added to `requirements.txt`; `dpr_technique.py` imports it and it was missing.

**Course (Udemy)**
- Section 3: new coding exercise "Classify Four Failure Traces", after "Deep Dive into Each Naive RAG Drawback".
- Section 3: new Role Play "Tell the PM Which Layer Broke", after that exercise.
- Section 8: new coding exercise "Implement a Bounded Retrieval Loop", after "Agentic RAG with LangGraph".
- Section 8: new Role Play "The CTO Read a Blog Post About GraphRAG", after "How to Choose an Advanced RAG Technique".

Day-30 read for the four new items: 2026-10-15 (participation and active minutes, matched exposure).
