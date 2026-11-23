SELECT load_date
FROM confluence_index.pipeline_state
WHERE pipeline_name = %(pipeline_name)s;
