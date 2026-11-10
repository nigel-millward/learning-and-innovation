SELECT page_id
FROM confluence_index.pages
WHERE status = 'active'
  AND indexed_at < %(indexed_before)s;
