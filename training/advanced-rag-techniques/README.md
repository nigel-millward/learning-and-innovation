<!-- @format -->
# Advanced RAG Techniques — Course Code

Source code for the **Advanced RAG Techniques** course on Udemy by Paulo Dichone. Every script here is
one you see built on screen. Run them in the order the course teaches them, against the same document
the course uses, and you will get the same results you see in the lectures.

**What the course covers:** you start with a naive RAG pipeline, watch it fail, and then fix it with
one technique at a time. Query expansion. Re-ranking with a cross-encoder. Dense passage retrieval.
Each technique gets its own script, and each script is self-contained so you can run it on its own.

## Setup

In this repo the course code lives in `training/advanced-rag-techniques/` (upstream:
`https://github.com/pdichone/advanced-rag-techniques`). Its Python environment is a
[uv](https://docs.astral.sh/uv/)-managed virtualenv **outside** the repo, at
`~/.virtualenv/advanced-rag-techniques-3.1.2/` (CPython 3.12). It has no `pip` of its own, so install
packages with `uv pip`:

```bash
cd training/advanced-rag-techniques
source ~/.virtualenv/advanced-rag-techniques-3.1.2/bin/activate
uv pip install -r requirements.txt    # picks up the active venv
```

To rebuild the environment from scratch:

```bash
uv venv --python 3.12 ~/.virtualenv/advanced-rag-techniques-3.1.2
source ~/.virtualenv/advanced-rag-techniques-3.1.2/bin/activate
uv pip install -r requirements.txt
```

Without activating, point `uv` at the interpreter instead:
`uv pip install --python ~/.virtualenv/advanced-rag-techniques-3.1.2/bin/python <package>`.

No API key and no `.env` file are needed. Every script runs its chat model locally on Ollama, and
embeddings are local `sentence-transformers`.

### Ollama (for `expansion_answer.py`, `expansion_queries.py` and `reranking.py`)

These scripts generate text with a local `llama3.2` model served by
[Ollama](https://ollama.com), called through LangChain's `ChatOllama` (`langchain-ollama`). This is
the same Ollama setup as `experiments/ai/01-llm-api`. No API key, no cost, and nothing leaves your
machine.

1. **Install Ollama** (macOS):

   ```bash
   brew install ollama
   ```

   Other platforms: download from [ollama.com/download](https://ollama.com/download).

2. **Start the server.** Leave this running in its own terminal. It listens on
   `http://localhost:11434`.

   ```bash
   ollama serve
   ```

   If you installed the Ollama desktop app, it starts the server for you and `ollama serve` will
   report the port is already in use. That is fine.

3. **Pull the model** (one-off, about 2 GB):

   ```bash
   ollama pull llama3.2
   ```

4. **Build the judge variant** (one-off, seconds; it reuses the `llama3.2` weights). Only
   `reranking.py` needs it, for its RAG Triad report:

   ```bash
   ollama create llama3.2-judge -f modelfiles/llama3.2-judge.Modelfile
   ```

   It raises the context to 16k tokens, because Ollama gives `llama3.2` 4096 by default and cuts
   longer prompts off without an error. It also caps each verdict at 512 tokens, so a judge reply
   that never ends costs seconds rather than minutes.

5. **Check it works:**

   ```bash
   ollama list                       # llama3.2 and llama3.2-judge should be listed
   curl http://localhost:11434/api/generate \
     -d '{"model": "llama3.2", "prompt": "What is Snowflake?", "stream": false}'
   ```

6. **Run the script** from this folder, with the venv active:

   ```bash
   source ~/.virtualenv/advanced-rag-techniques-3.1.2/bin/activate
   python expansion_answer.py
   ```

   The script ends by opening a matplotlib window with the embedding plot. It waits there until you
   close the window. To run it without a window (for example over SSH), use
   `MPLBACKEND=Agg python expansion_answer.py`.

The server URL, model and timeout are constants at the top of each script
(`OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `TIMEOUT_SECONDS`). To try another model, `ollama pull <name>`
and change `OLLAMA_MODEL`. Stop the server with `Ctrl+C` in its terminal (or quit the desktop app).

The first run of `reranking.py` and `dpr_technique.py` downloads models from Hugging Face. Expect a
few minutes and a couple of GB the first time; after that they load from cache.

## Which script goes with which section

| Course section | Script | What it does |
|---|---|---|
| 4 · Query Expansion with Generated Answers | `expansion_answer.py` | Asks the LLM for a hypothetical answer, appends it to the query, and retrieves with the joint query. Plots the original vs augmented query in embedding space |
| 5 · Query Expansion with Multiple Queries | `expansion_queries.py` | Asks the LLM for five related questions, retrieves for all of them, and de-duplicates the union |
| 6 · Re-Ranking with a Cross-Encoder | `reranking.py` | Retrieves a wide candidate set, then re-scores every candidate with `cross-encoder/ms-marco-MiniLM-L-6-v2` before generating the answer, then prints a TruLens RAG Triad report. The example of a script using `trulens_utils.py` |
| 7 · Dense Passage Retrieval | `dpr_technique.py` | Encodes questions and passages with Facebook's DPR question and context encoders and ranks by cosine similarity |
| shared | `helper_utils.py` | PDF text extraction, Chroma loading, text wrapping, UMAP projection for the embedding plots |
| shared | `trulens_utils.py` | TruLens RAG Triad metrics (context relevance, groundedness, answer relevance, each 0 to 1; closer to 1 is better), the recorder a script wraps its pipeline in, and the terminal report. Used by `reranking.py` |

Sections 1 to 3 (setup, RAG fundamentals, the RAG triad, naive RAG and its drawbacks) are concept
lectures and have no separate script. Section 8 (contextual retrieval, late chunking, agentic RAG,
GraphRAG, multimodal RAG) ships its code as downloadable resources attached to those lectures.

## The data

`data/microsoft-annual-report.pdf` is the one document every script indexes. Using the same corpus
throughout is deliberate: when a technique changes what gets retrieved, you know the technique did
it, not the data.

Each script re-reads the PDF, chunks it, and builds a fresh in-memory Chroma collection on every run.
There is nothing to clean up between runs.

## The stack

| Piece | What the code uses |
|---|---|
| Chat model | Local Ollama `llama3.2` via LangChain `ChatOllama`, in `expansion_answer.py`, `expansion_queries.py` and `reranking.py` (`OLLAMA_MODEL` constant; change it there) |
| Embeddings | Local `sentence-transformers` via Chroma's default embedding function. No API key needed for retrieval |
| Vector store | Chroma, in memory |
| Re-ranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` from `sentence-transformers` |
| Evaluation | [TruLens](https://www.trulens.org) RAG Triad, defined in `trulens_utils.py` and recorded by `reranking.py`. Judged by local Ollama `llama3.2-judge` through `trulens-providers-litellm` (`EVALUATION_MODEL` in `trulens_utils.py`). Every run is stored in `trulens.sqlite`, and the report's leaderboard compares runs and `APP_VERSION`s |
| DPR | `facebook/dpr-question_encoder-single-nq-base` and `facebook/dpr-ctx_encoder-single-nq-base` from `transformers` |
| Chunking | LangChain `RecursiveCharacterTextSplitter` then `SentenceTransformersTokenTextSplitter` |

**Model note, October 2026.** The scripts used to call OpenAI and default to `gpt-3.5-turbo`, which
OpenAI is retiring on 23 October 2026. They now all run a local Ollama model instead and no longer
call OpenAI, so no API key is needed. To use a different local model, `ollama pull <name>` and
change the `OLLAMA_MODEL` constant at the top of the script.

## Running the scripts

Run from this folder with the venv active:

```bash
source ~/.virtualenv/advanced-rag-techniques-3.1.2/bin/activate
python expansion_answer.py
python expansion_queries.py
python reranking.py
python dpr_technique.py
```

Each script prints the query, the retrieved chunks, and the generated answer so you can compare
the retrieval before and after the technique is applied. Lines that are commented out in the source
are the intermediate prints used on screen in the lectures; uncomment them to follow along.

## Troubleshooting

- **`could not connect to Ollama at http://localhost:11434`.** The Ollama server is not running. Start it with `ollama serve` (or open the Ollama app) and re-run.
- **`Ollama returned 404: model 'llama3.2' not found`.** The model has not been pulled. Run `ollama pull llama3.2`.
- **`Ollama did not respond within 60s`.** The first request after starting loads the model into memory and can be slow on a laptop. Re-run, or raise `TIMEOUT_SECONDS` in the script you are running.
- **`Ollama returned 404 for judge model 'llama3.2-judge'`.** The judge variant has not been built. Run `ollama create llama3.2-judge -f modelfiles/llama3.2-judge.Modelfile`.
- **A score shows `NaN`.** The judge gave no reply TruLens could parse for that metric, so TruLens left it out rather than guess. Re-run; a stronger judge (set `EVALUATION_MODEL` in `trulens_utils.py`) makes it rarer.
- **The leaderboard mixes old and new results.** It averages every run in `trulens.sqlite`. Bump `APP_VERSION` in `reranking.py` when you change its settings, or delete `trulens.sqlite` to start over.
- **`ModuleNotFoundError: No module named 'trulens'`.** Run `uv pip install -r requirements.txt` with the venv active. The first groundedness run also downloads NLTK's `punkt_tab` sentence tokenizer.
- **`No module named pip`.** Expected: the venv is uv-managed. Use `uv pip install ...` rather than `pip install ...`.
- **`ModuleNotFoundError: No module named 'langchain_ollama'`.** The venv predates the Ollama switch. Run `uv pip install -r requirements.txt` with the venv active.
- **Slow first run.** Model downloads from Hugging Face. Subsequent runs are fast.
- **`torch` install trouble.** Install the CPU build from pytorch.org for your platform, then re-run `uv pip install -r requirements.txt`.
- **Different chunk counts than the video.** Library versions drift. The retrieval behaviour is what matters, not the exact number.

---

## Go further: The AI Guild

This code is part of a module in [The AI Guild](https://bit.ly/ai-guild-join), a community of
developers and entrepreneurs building real AI tools together. Weekly live calls, code and template
vault, guided learning paths from the basics through production systems, and direct feedback on
what you build. All skill levels welcome.
