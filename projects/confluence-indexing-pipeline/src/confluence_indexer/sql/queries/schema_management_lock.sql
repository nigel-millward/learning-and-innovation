-- Serialises concurrent schema management (e.g. a DAG run and a local run racing).
SELECT pg_advisory_lock(hashtext('confluence_indexer_schema_management'));
