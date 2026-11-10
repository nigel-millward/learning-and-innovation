-- Declared type of chunks.embedding, e.g. 'vector(768)', checked against EMBEDDING_DIMENSIONS.
SELECT format_type(a.atttypid, a.atttypmod) AS column_type
FROM pg_attribute AS a
WHERE a.attrelid = 'confluence_index.chunks'::regclass
  AND a.attname = 'embedding';
