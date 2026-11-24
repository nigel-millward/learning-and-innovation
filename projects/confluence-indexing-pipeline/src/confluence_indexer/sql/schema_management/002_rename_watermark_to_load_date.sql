-- Rename pipeline_state.watermark to load_date, the team's standard name for
-- this column. 001 now creates load_date directly; this renames it only in
-- databases created before that change, and does nothing otherwise.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'confluence_index'
          AND table_name = 'pipeline_state'
          AND column_name = 'watermark'
    ) THEN
        ALTER TABLE confluence_index.pipeline_state RENAME COLUMN watermark TO load_date;
    END IF;
END
$$;

COMMENT ON COLUMN confluence_index.pipeline_state.load_date IS
    'Start time of the last successful run. Moves forward only; extract re-reads from here minus an overlap.';
