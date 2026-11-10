# Confluence indexing pipeline

Daily, incremental indexing of Confluence pages into PostgreSQL + pgvector for
retrieval-augmented generation. **Apache Airflow 3** schedules and orchestrates it.
Only pages changed since the last successful run are fetched, and only chunks
whose text actually changed are re-embedded.

```
extract -> transform -> load -> commit_watermark --> publish_run_status
                             \-> reconcile -------/
```

| Task | What it does |
|---|---|
| `extract` | CQL search `lastmodified >= watermark - overlap`; skips versions already indexed; adds dead-lettered pages due a retry; lands each raw page in S3 (`raw/space=/page_id=/version=.json`). |
| `transform` | Converts storage-format XHTML to clean Markdown-ish text (drops TOC/page-tree/child/include macros, media, macro params, ADF fallbacks, boilerplate, repeated blocks) and chunks it with `RecursiveCharacterTextSplitter` (800 tokens, 120 overlap = 15%, heading-aware). Stages `documents.jsonl` in S3. |
| `load` | Hashes each chunk (`sha256` of contextual header + text), reuses any existing vector with that hash and embedding version, embeds the rest, and replaces the page's rows in one transaction. Emits the `confluence_index` Airflow asset. |
| `commit_watermark` | Advances the watermark (forward-only) to the extract start time, only after a successful load. |
| `reconcile` | Compares every live page ID with the index and removes vectors for deleted or no-longer-visible pages. A mass-deletion guard stops a permissions fault from emptying the index. |
| `publish_run_status` | Always runs. Publishes CloudWatch metrics, writes a `pipeline_runs` audit row, sends an SNS warning on degraded success, and fails the DAG run if any stage failed. Task failures send their own SNS alert with the exception. |

## Layout

```
src/confluence_indexer/
├── dags/confluence_indexing.py   Airflow 3 DAG: schedule, retries, params, alerts, asset
├── tasks.py                      Body of each Airflow task: builds real clients, runs a stage
├── stages/                       One module per stage; pure orchestration logic, no Airflow
│   ├── base.py                   StageReport, failure budget, dead-lettering
│   ├── extract.py  transform.py  load.py  reconcile.py  watermark.py  summary.py
├── integrations/                 Adapters that do I/O (replaced by fakes in tests)
│   ├── confluence.py             REST client: CQL search, pagination, retry/backoff
│   ├── landing_zone.py           S3 raw pages, run manifests, staged JSONL
│   ├── vector_store.py           pgvector store; executes SQL from sql/
│   ├── embeddings.py             Ollama, OpenAI, Azure OpenAI, Bedrock Titan
│   └── observability.py          CloudWatch metrics, SNS alerts
├── processing/                   Pure text transforms, no I/O
│   ├── cleaning.py  chunking.py
├── sql/
│   ├── queries/*.sql             Every statement the store runs (named parameters)
│   └── migrations/*.sql          Schema DDL, applied in order
├── config.py  models.py  cli.py
deployment/                       docker-compose (pgvector + LocalStack)
tests/
```

`integrations/` holds code that does I/O and `processing/` holds pure functions.
That tells you what to fake in a test, and avoids a catch-all `libs/`.

## Data model (`confluence_index` schema)

| Table | Purpose |
|---|---|
| `chunks` | `chunk_id` (`{page_id}:{index}`), `page_id`, `content`, `embedding_text`, `content_hash`, `embedding_version`, `embedding vector(N)`, `metadata` jsonb. This is the page/chunk/hash/embedding-version mapping. HNSW cosine index. |
| `pages` | Source registry: version, last modified, labels, ancestors, page content hash, raw S3 URI. Soft-deleted on removal. |
| `pipeline_state` | The watermark. |
| `failed_pages` | Dead letters: retried each run until `MAX_PAGE_ATTEMPTS`, then parked (and counted in CloudWatch). |
| `pipeline_runs` | One audit row per DAG run. |

`embedding_version` is `provider:model:dimensions:revision`. Vectors are only
reused within the same version, so changing the model can never mix vector spaces.

## Run it locally

Prerequisites: Docker, [Ollama](https://ollama.com) (`brew install ollama`), Python 3.11+,
and a Confluence site with an API token. Confluence has no local emulator, so the
extract stage always calls a real site.

```bash
cd projects/confluence-indexing-pipeline
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,airflow]"

ollama serve &                       # if not already running
ollama pull nomic-embed-text         # 768-dimension embeddings, no API key

docker compose -f deployment/docker-compose.yml up -d   # pgvector + LocalStack
cp .env.example .env                 # then fill in the CONFLUENCE_* values
set -a && source .env && set +a

confluence-indexer migrate           # creates the schema with vector(768)
```

**With Airflow 3** (the real orchestrator):

```bash
export AIRFLOW_HOME=$PWD/airflow-home
export AIRFLOW__CORE__DAGS_FOLDER=$PWD/src/confluence_indexer/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
airflow standalone                   # UI on http://localhost:8080; trigger confluence_indexing
```

**Without Airflow**, the CLI runs the same task functions in-process:

```bash
confluence-indexer run               # one incremental run
confluence-indexer run --full-refresh
confluence-indexer replay s3://confluence-indexing-landing/confluence-indexing/runs/run_id=<id>/extract_manifest.json
```

## Tests

```bash
pytest                                # unit tests; Confluence, S3 (moto) and the store are faked
ruff check . && ruff format --check . && mypy src
PGVECTOR_TEST_DSN=postgresql://indexer:indexer@localhost:5433/postgres pytest -m integration
```

`tests/test_dag.py` parses the DAG with a real Airflow 3 `DagBag`. It is
skipped when Airflow is not installed.

## Configuration

All settings are environment variables; `.env.example` lists them with local
values. In Airflow, credentials are taken from these Connections when they exist,
and from the environment otherwise:

| Connection | Fields used |
|---|---|
| `confluence_default` | host = base URL (`https://site.atlassian.net/wiki`), login = email, password = API token |
| `pgvector_default` | full URI, e.g. `postgresql://user:pass@host:5432/db?sslmode=verify-full` |
| `openai_default` | password = API key (only when `EMBEDDING_PROVIDER=openai`) |

Outside Airflow, any secret can instead be given as `<NAME>_SECRET_ID` pointing at
AWS Secrets Manager. `PG_DSN_SECRET_ID` also accepts an RDS-managed secret.

## Operations

| Situation | Action |
|---|---|
| A page keeps failing | `SELECT * FROM confluence_index.failed_pages;` shows the error. Fix it and the next run retries automatically. To retry a parked page, `UPDATE ... SET attempts = 0`. |
| `DeletionGuardError` | Reconcile would delete more than `MAX_DELETE_RATIO` of the index. Check the service account's space permissions. If the deletions are real, trigger with `allow_mass_delete=true`. |
| Cleaning or chunking rules changed | Trigger with `full_refresh=true`. Only chunks whose text changed are re-embedded. |
| Re-process a past run without calling Confluence | `confluence-indexer replay <extract_manifest.json URI>`. |
| Changing embedding model or dimensions | The vector column size is fixed at migrate time. For a new dimension, create a fresh schema (or database), set `EMBEDDING_*`, run `migrate`, then `full_refresh=true`. For the same dimension, bump `EMBEDDING_REVISION` and `full_refresh`. |

Suggested CloudWatch alarms on namespace `ConfluenceIndexing`:
`RunSucceeded` < 1 over 26 hours, treating missing data as breaching (this catches a
scheduler that stopped running); `DeadLetterParkedPages` > 0; `LoadPagesFailed` > 0.

## Design notes

- **Deletions:** CQL cannot return deleted pages, so `reconcile` diffs the full
  list of live page IDs against the index. Pages indexed during the current run are
  excluded, to avoid racing Confluence's eventually consistent search index.
- **Watermark overlap:** CQL dates have minute precision and use the API user's
  timezone, and search indexing lags. Each run therefore re-reads a 30-minute
  overlap, and version checks make that re-read close to free.
- **Cost control:** a page whose content hash is unchanged is never re-embedded.
  Within a changed page, a chunk is re-embedded only if its hash is new anywhere in
  the index, so moved and duplicated text reuses existing vectors.
- **Failure policy:** a bad page is dead-lettered and does not block the
  watermark. A stage fails, and Airflow retries it, only when more than
  `MAX_FAILURE_RATIO` of its pages fail. Retries are idempotent.
