SELECT page_id, version, content_hash, embedding_version
FROM confluence_index.pages
WHERE page_id = ANY(%(page_ids)s)
  AND status = 'active';
