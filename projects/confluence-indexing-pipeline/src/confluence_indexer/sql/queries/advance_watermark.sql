-- Moves the watermark forward only: a late or stale run can never rewind it.
INSERT INTO confluence_index.pipeline_state (pipeline_name, watermark, last_run_id)
VALUES (%(pipeline_name)s, %(watermark)s, %(run_id)s)
ON CONFLICT (pipeline_name) DO UPDATE SET
    watermark = GREATEST(pipeline_state.watermark, EXCLUDED.watermark),
    last_run_id = EXCLUDED.last_run_id,
    updated_at = now()
RETURNING watermark;
