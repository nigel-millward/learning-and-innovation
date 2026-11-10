DELETE FROM confluence_index.failed_pages
WHERE page_id = ANY(%(page_ids)s);
