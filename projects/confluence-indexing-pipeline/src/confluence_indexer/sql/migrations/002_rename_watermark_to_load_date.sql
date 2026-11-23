-- Rename pipeline_state.watermark to load_date, the team's standard name for
-- this column. 001 is left unchanged because databases that have already run it
-- are not migrated again.
ALTER TABLE confluence_index.pipeline_state RENAME COLUMN watermark TO load_date;

COMMENT ON COLUMN confluence_index.pipeline_state.load_date IS
    'Start time of the last successful run. Moves forward only; extract re-reads from here minus an overlap.';
