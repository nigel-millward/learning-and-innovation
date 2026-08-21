/*
  Technique: Zero-Copy Clone (instant dev/test environments)
  ----------------------------------------------------------
  Snowflake's CLONE creates a new database/schema/table that shares the source's
  existing micro-partitions instead of copying the data. The clone is available
  instantly and consumes no extra storage until rows diverge (copy-on-write).

  Why it is useful: spinning up a dev or test schema by re-loading or CTAS-ing
  production data is slow and doubles storage. A zero-copy clone gives an
  engineer a full, writable copy of production in seconds for near-zero cost,
  and only the rows they change ever take up additional storage.

  Usage (run as an operation, not during a normal run):
    dbt run-operation zero_copy_clone \
      --args '{source_schema: SDP_GOLD.SQL_OPTIMISATIONS, target_schema: SDP_GOLD.SQL_OPTIMISATIONS_DEV}'
*/
{% macro zero_copy_clone(source_schema, target_schema) %}
    {% set clone_sql %}
        -- Optimised line: CLONE shares the source's micro-partitions (copy-on-write) instead of copying data
        CREATE OR REPLACE SCHEMA {{ target_schema }} CLONE {{ source_schema }}
    {% endset %}
    {% do run_query(clone_sql) %}
    {% do log("Zero-copy cloned " ~ source_schema ~ " into " ~ target_schema, info=true) %}
{% endmacro %}
