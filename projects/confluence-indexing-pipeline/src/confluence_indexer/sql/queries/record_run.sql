INSERT INTO confluence_index.pipeline_runs (run_id, pipeline_name, status, stats, failed_stages)
VALUES (%(run_id)s, %(pipeline_name)s, %(status)s, %(stats)s, %(failed_stages)s)
ON CONFLICT (pipeline_name, run_id) DO UPDATE SET
    status = EXCLUDED.status,
    stats = EXCLUDED.stats,
    failed_stages = EXCLUDED.failed_stages,
    recorded_at = now();
