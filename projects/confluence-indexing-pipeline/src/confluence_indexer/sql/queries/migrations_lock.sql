-- Serialises concurrent migrators (e.g. two deploys racing).
SELECT pg_advisory_lock(hashtext('confluence_indexer_migrations'));
