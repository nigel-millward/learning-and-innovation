-- Rows whose hash, embedding version and metadata are unchanged are left
-- untouched, so the HNSW index is not churned by no-op rewrites.
INSERT INTO confluence_index.chunks (
    chunk_id, page_id, chunk_index, content, embedding_text, content_hash,
    token_count, embedding_version, embedding, metadata
) VALUES (
    %(chunk_id)s, %(page_id)s, %(chunk_index)s, %(content)s, %(embedding_text)s,
    %(content_hash)s, %(token_count)s, %(embedding_version)s, %(embedding)s, %(metadata)s
)
ON CONFLICT (chunk_id) DO UPDATE SET
    content = EXCLUDED.content,
    embedding_text = EXCLUDED.embedding_text,
    content_hash = EXCLUDED.content_hash,
    token_count = EXCLUDED.token_count,
    embedding_version = EXCLUDED.embedding_version,
    embedding = EXCLUDED.embedding,
    metadata = EXCLUDED.metadata,
    updated_at = now()
WHERE chunks.content_hash IS DISTINCT FROM EXCLUDED.content_hash
   OR chunks.embedding_version IS DISTINCT FROM EXCLUDED.embedding_version
   OR chunks.metadata IS DISTINCT FROM EXCLUDED.metadata;
