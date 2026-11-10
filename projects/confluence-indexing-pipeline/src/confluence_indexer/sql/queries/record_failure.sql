INSERT INTO confluence_index.failed_pages (page_id, stage, last_error, last_run_id)
VALUES (%(page_id)s, %(stage)s, %(error)s, %(run_id)s)
ON CONFLICT (page_id) DO UPDATE SET
    stage = EXCLUDED.stage,
    attempts = failed_pages.attempts + 1,
    last_error = EXCLUDED.last_error,
    last_failed_at = now(),
    last_run_id = EXCLUDED.last_run_id;
