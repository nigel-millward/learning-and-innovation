DELETE FROM confluence_index.chunks
WHERE page_id = ANY(%(page_ids)s);
