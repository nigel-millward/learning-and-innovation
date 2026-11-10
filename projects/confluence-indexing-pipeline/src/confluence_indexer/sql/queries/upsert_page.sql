INSERT INTO confluence_index.pages (
    page_id, space_key, title, url, version, last_modified, last_modified_by,
    labels, ancestors, content_hash, embedding_version, chunk_count, raw_uri
) VALUES (
    %(page_id)s, %(space_key)s, %(title)s, %(url)s, %(version)s, %(last_modified)s,
    %(last_modified_by)s, %(labels)s, %(ancestors)s, %(content_hash)s,
    %(embedding_version)s, %(chunk_count)s, %(raw_uri)s
)
ON CONFLICT (page_id) DO UPDATE SET
    space_key = EXCLUDED.space_key,
    title = EXCLUDED.title,
    url = EXCLUDED.url,
    version = EXCLUDED.version,
    last_modified = EXCLUDED.last_modified,
    last_modified_by = EXCLUDED.last_modified_by,
    labels = EXCLUDED.labels,
    ancestors = EXCLUDED.ancestors,
    content_hash = EXCLUDED.content_hash,
    embedding_version = EXCLUDED.embedding_version,
    chunk_count = EXCLUDED.chunk_count,
    raw_uri = EXCLUDED.raw_uri,
    status = 'active',
    deleted_at = NULL,
    indexed_at = now();
