-- Advances the load_date forward only: a late or stale run can never rewind it.
INSERT INTO confluence_index.pipeline_state (pipeline_name, load_date, last_run_id)
VALUES (%(pipeline_name)s, %(load_date)s, %(run_id)s)
ON CONFLICT (pipeline_name) DO UPDATE SET
    load_date = GREATEST(pipeline_state.load_date, EXCLUDED.load_date),
    last_run_id = EXCLUDED.last_run_id,
    updated_at = now()
RETURNING load_date;
