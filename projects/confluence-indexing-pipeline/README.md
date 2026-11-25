# Confluence indexing pipeline

Daily, incremental indexing of Confluence pages into PostgreSQL + pgvector for
retrieval-augmented generation. **Apache Airflow 3** schedules and orchestrates it.
Only pages changed since the last successful run are fetched, and only chunks
whose text actually changed are re-embedded.

```
schema_management -> extract -> transform -> load -> commit_watermark --> publish_run_status
                                                  \-> reconcile -------/
```

| Task | What it does |
|---|---|
| `schema_management` | Runs `sql/schema_management/*.sql` in order: creates the schema, tables and indexes if they don't exist. Every statement is rerunnable, so existing objects and data are kept. A new schema change must be written the same way (`IF NOT EXISTS`, or guarded in a `DO` block). |
| `extract` | CQL search `lastmodified >= load_date - overlap`; skips versions already indexed; adds dead-lettered pages due a retry; lands each raw page in S3 (`raw/space=/page_id=/version=.json`). |
| `transform` | Converts storage-format XHTML to clean Markdown-ish text (drops TOC/page-tree/child/include macros, media, macro params, ADF fallbacks, boilerplate, repeated blocks) and chunks it with `RecursiveCharacterTextSplitter` (800 tokens, 120 overlap = 15%, heading-aware). Stages `documents.jsonl` in S3. |
| `load` | Hashes each chunk (`sha256` of contextual header + text), reuses any existing vector with that hash and embedding version, embeds the rest, and replaces the page's rows in one transaction. Emits the `confluence_index` Airflow asset. |
| `commit_watermark` | Advances the load_date (forward-only) to the extract start time, only after a successful load. |
| `reconcile` | Compares every live page ID with the index and removes vectors for deleted or no-longer-visible pages. A mass-deletion guard stops a permissions fault from emptying the index. |
| `publish_run_status` | Always runs. Publishes CloudWatch metrics, writes a `pipeline_runs` audit row, sends an SNS warning on degraded success, and fails the DAG run if any stage failed. Task failures send their own SNS alert with the exception. |

## Layout

```
src/confluence_indexer/
├── confluence_indexing_dag.py    Daily DAG: schedule, retries, params, task order, asset
├── .airflowignore                Only *_dag.py files are parsed as DAGs
├── orchestration/                Runs the stages under Airflow
│   ├── airflow_runtime.py        Airflow plumbing for the DAGs: config, run context, XCom keys, alerts
│   └── tasks.py                  One run_* per task: builds real clients, runs it (no Airflow)
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
│   └── schema_management/*.sql   Rerunnable schema DDL, applied in order on every run
├── config.py  models.py          Shared config and models
scripts/run_pipeline_locally.py   Developer tool: runs the task functions in DAG order, no Airflow
deployment/                       docker-compose (pgvector + LocalStack)
tests/
├── conftest.py                   Shared fakes and fixtures
├── unit/                         No external services; Confluence, S3 (moto) and the store are faked
└── integration/                  Needs a live PostgreSQL with pgvector
```

`integrations/` holds code that does I/O and `processing/` holds pure functions.
That tells you what to fake in a test, and avoids a catch-all `libs/`.

## Data model (`confluence_index` schema)

| Table | Purpose |
|---|---|
| `chunks` | `chunk_id` (`{page_id}:{index}`), `page_id`, `content`, `embedding_text`, `content_hash`, `embedding_version`, `embedding vector(N)`, `metadata` jsonb. This is the page/chunk/hash/embedding-version mapping. HNSW cosine index. |
| `pages` | Source registry: version, last modified, labels, ancestors, page content hash, raw S3 URI. Soft-deleted on removal. |
| `pipeline_state` | The load_date. |
| `failed_pages` | Dead letters: retried each run until `MAX_PAGE_ATTEMPTS`, then parked (and counted in CloudWatch). |
| `pipeline_runs` | One audit row per DAG run. |

`embedding_version` is `provider:model:dimensions:revision`. Vectors are only
reused within the same version, so changing the model can never mix vector spaces.

## Extract manifest and raw page example

Each extract run writes its own `extract_manifest.json`. Its `pages` array has
one entry for each page successfully fetched and saved during that run. A daily
incremental run includes pages that need fetching because they changed (including
the load-date overlap) and retryable failures; unchanged, vanished, or failed
pages do not get entries. Thus, it lists the pages extracted by that run, not
every page in Confluence. A full refresh fetches every page returned by the
Confluence search.

The manifest stores page IDs, versions, and S3 URIs; the page payload is stored
separately at each `raw_uri`. `transform` reads that payload from S3 for each
entry. The following sample shows five successful entries:

```json
{
  "run_id": "scheduled__2026-11-25T02:00:00+00:00",
  "run_started_at": "2026-11-25T02:00:01+00:00",
  "since": "2026-11-24T01:30:00+00:00",
  "full_refresh": false,
  "embedding_version": "ollama:nomic-embed-text:768:r1",
  "pages": [
    {
      "page_id": "1001",
      "version": 1,
      "raw_uri": "s3://confluence-indexing-landing/confluence-indexing/raw/space=ENG/page_id=1001/version=1.json"
    },
    {
      "page_id": "1002",
      "version": 3,
      "raw_uri": "s3://confluence-indexing-landing/confluence-indexing/raw/space=ENG/page_id=1002/version=3.json"
    },
    {
      "page_id": "1003",
      "version": 2,
      "raw_uri": "s3://confluence-indexing-landing/confluence-indexing/raw/space=ENG/page_id=1003/version=2.json"
    },
    {
      "page_id": "1004",
      "version": 1,
      "raw_uri": "s3://confluence-indexing-landing/confluence-indexing/raw/space=ENG/page_id=1004/version=1.json"
    },
    {
      "page_id": "1005",
      "version": 4,
      "raw_uri": "s3://confluence-indexing-landing/confluence-indexing/raw/space=ENG/page_id=1005/version=4.json"
    }
  ]
}
```

For example, `page_id=1001/version=1.json` contains an envelope with the original
Confluence page under `payload`:

```json
{
  "schema_version": 1,
  "source": "confluence",
  "run_id": "scheduled__2026-11-25T02:00:00+00:00",
  "extracted_at": "2026-11-25T02:00:02+00:00",
  "payload": {
    "id": "1001",
    "type": "page",
    "status": "current",
    "title": "Deployment runbook",
    "space": {
      "key": "ENG",
      "name": "Engineering"
    },
    "version": {
      "number": 1,
      "when": "2026-11-25T01:45:00.000Z",
      "by": {
        "displayName": "Ada"
      }
    },
    "ancestors": [
      {
        "id": "1",
        "title": "Engineering Home"
      }
    ],
    "metadata": {
      "labels": {
        "results": [
          {
            "name": "runbook"
          }
        ]
      }
    },
    "body": {
      "storage": {
        "value": "<p>Steps for deploying the service.</p>",
        "representation": "storage"
      }
    },
    "_links": {
      "webui": "/spaces/ENG/pages/1001",
      "base": "https://example.atlassian.net/wiki"
    }
  }
}
```

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
```

**While developing, without Airflow:** `scripts/run_pipeline_locally.py` calls the
same `run_*` task functions as the DAG, in DAG order. It is a developer tool, not
deployed and not a test. Breakpoints work in a normal debugger.

```bash
python scripts/run_pipeline_locally.py                  # schema management, then one incremental run
python scripts/run_pipeline_locally.py --full-refresh   # re-read every page
python scripts/run_pipeline_locally.py --replay s3://confluence-indexing-landing/confluence-indexing/runs/run_id=<id>/extract_manifest.json
python scripts/run_pipeline_locally.py --help           # --skip-schema-management, --allow-mass-delete, --log-level
```

**Before deploying, with Airflow** (exercises XComs, params and task order too):

```bash
export AIRFLOW_HOME=$PWD/airflow-home
export AIRFLOW__CORE__DAGS_FOLDER=$PWD/src/confluence_indexer
export AIRFLOW__CORE__LOAD_EXAMPLES=False
airflow db migrate                   # one-off: local SQLite metadata database

airflow dags test confluence_indexing   # one run, in-process, no scheduler; creates the schema with vector(768) first
airflow standalone                   # or the full UI on http://localhost:8080
```

On MWAA, copy the `src/confluence_indexer/` folder (including `.airflowignore`)
into the environment's S3 `dags/` folder. The first run creates the schema; the
database user needs rights to create the schema and the `vector` extension, or a
DBA can run `sql/schema_management/*.sql` once beforehand.

## Tests

```bash
pytest tests/unit                     # unit tests; Confluence, S3 (moto) and the store are faked
ruff check . && ruff format --check . && mypy src scripts
PGVECTOR_TEST_DSN=postgresql://indexer:indexer@localhost:5433/postgres pytest tests/integration
```

`pytest` with no arguments runs both folders; the integration tests skip when
`PGVECTOR_TEST_DSN` is not set.

`tests/unit/test_dag.py` parses the DAG with a real Airflow 3 `DagBag`, scanning
the package the way Airflow does. It is skipped when Airflow is not installed.

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
| Re-process a past run without calling Confluence | In the Airflow UI, open that `confluence_indexing` run, select `transform` and `load` and **Clear** them with "Downstream" unticked. They re-read that run's extract manifest from XCom, so this only works while the run's XComs still exist (`airflow db clean` removes them). |
| Changing embedding model or dimensions | The vector column size is fixed when `schema_management` first creates `chunks`. For a new dimension, create a fresh schema (or database), set `EMBEDDING_*`, then trigger with `full_refresh=true`; the run recreates the schema first. For the same dimension, bump `EMBEDDING_REVISION` and `full_refresh`. |

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
  load_date. A stage fails, and Airflow retries it, only when more than
  `MAX_FAILURE_RATIO` of its pages fail. Retries are idempotent.
