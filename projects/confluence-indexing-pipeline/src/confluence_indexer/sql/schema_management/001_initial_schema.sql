-- Schema for the Confluence vector index.
--
-- Runs at the start of every pipeline run, so every statement must be safe to
-- rerun: create objects with IF NOT EXISTS and never drop or rewrite data here.
--
-- :embedding_dimensions is substituted from EMBEDDING_DIMENSIONS by
-- apply_schema_management (or pass `psql -v embedding_dimensions=768`).
-- It must match the embedding model: 768 for Ollama nomic-embed-text, 1536 for
-- text-embedding-3-large with dimensions=1536, 1024 for Titan v2. pgvector cannot
-- build an HNSW index on `vector` above 2000 dimensions; beyond that use halfvec.
-- An existing chunks table keeps its size; the load stage checks this column
-- against EMBEDDING_DIMENSIONS and fails rather than mixing dimensions.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE SCHEMA IF NOT EXISTS confluence_index;

-- Incremental extraction load_date, one row per pipeline.
CREATE TABLE IF NOT EXISTS confluence_index.pipeline_state (
    pipeline_name text PRIMARY KEY,
    load_date     timestamptz NOT NULL,
    last_run_id   text NOT NULL,
    updated_at    timestamptz NOT NULL DEFAULT now()
);

-- One row per DAG run, for audit and troubleshooting.
CREATE TABLE IF NOT EXISTS confluence_index.pipeline_runs (
    run_id        text NOT NULL,
    pipeline_name text NOT NULL,
    status        text NOT NULL CHECK (status IN ('success', 'failed')),
    stats         jsonb NOT NULL DEFAULT '{}'::jsonb,
    failed_stages text[] NOT NULL DEFAULT '{}',
    recorded_at   timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (pipeline_name, run_id)
);

-- Source page registry. Rows are soft-deleted so removals stay auditable.
CREATE TABLE IF NOT EXISTS confluence_index.pages (
    page_id           text PRIMARY KEY,
    space_key         text NOT NULL,
    title             text NOT NULL,
    url               text NOT NULL,
    version           integer NOT NULL,
    last_modified     timestamptz NOT NULL,
    last_modified_by  text,
    labels            text[] NOT NULL DEFAULT '{}',
    ancestors         text[] NOT NULL DEFAULT '{}',
    content_hash      text NOT NULL,
    embedding_version text NOT NULL,
    chunk_count       integer NOT NULL,
    raw_uri           text NOT NULL,
    status            text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deleted')),
    indexed_at        timestamptz NOT NULL DEFAULT now(),
    deleted_at        timestamptz
);

CREATE INDEX IF NOT EXISTS pages_active_space_idx ON confluence_index.pages (space_key) WHERE status = 'active';

-- Chunk text, vectors and the page/chunk/hash/embedding-version mapping.
CREATE TABLE IF NOT EXISTS confluence_index.chunks (
    chunk_id          text PRIMARY KEY,           -- "{page_id}:{chunk_index:05d}"
    page_id           text NOT NULL REFERENCES confluence_index.pages (page_id) ON DELETE CASCADE,
    chunk_index       integer NOT NULL,
    content           text NOT NULL,              -- chunk body returned to callers
    embedding_text    text NOT NULL,              -- header + body, exactly what was embedded
    content_hash      text NOT NULL,              -- sha256(embedding_text)
    token_count       integer NOT NULL,
    embedding_version text NOT NULL,              -- provider:model:dims:revision
    embedding         vector(:embedding_dimensions) NOT NULL,
    metadata          jsonb NOT NULL,             -- title, space, url, labels, section path...
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),
    UNIQUE (page_id, chunk_index)
);

-- Embedding reuse lookup: unchanged text is never sent to the embedding API twice.
CREATE INDEX IF NOT EXISTS chunks_hash_idx ON confluence_index.chunks (content_hash, embedding_version);

CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx ON confluence_index.chunks
    USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS chunks_metadata_idx ON confluence_index.chunks USING gin (metadata jsonb_path_ops);

-- Pages that failed a stage. They are retried on later runs until they succeed
-- or reach MAX_PAGE_ATTEMPTS, so one bad page never blocks the watermark.
CREATE TABLE IF NOT EXISTS confluence_index.failed_pages (
    page_id          text PRIMARY KEY,
    stage            text NOT NULL,
    attempts         integer NOT NULL DEFAULT 1,
    last_error       text NOT NULL,
    first_failed_at  timestamptz NOT NULL DEFAULT now(),
    last_failed_at   timestamptz NOT NULL DEFAULT now(),
    last_run_id      text NOT NULL
);
