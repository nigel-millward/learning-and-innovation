-- Chunks beyond the page's new length (the page got shorter).
DELETE FROM confluence_index.chunks
WHERE page_id = %(page_id)s
  AND chunk_index >= %(chunk_count)s;
