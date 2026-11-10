-- Pages are kept (status = 'deleted') so removals stay auditable.
UPDATE confluence_index.pages
SET status = 'deleted', deleted_at = now(), chunk_count = 0
WHERE page_id = ANY(%(page_ids)s)
  AND status = 'active';
