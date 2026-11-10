CREATE TABLE IF NOT EXISTS public.confluence_indexer_migrations (
    name       text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);
