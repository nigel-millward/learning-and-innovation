/*
  Transformation: Unpivoting (wide -> long)
  -----------------------------------------
  Unpivoting is the inverse of pivoting: it folds several columns down into
  rows, producing a (key, attribute_name, attribute_value) shape. Each input
  column becomes a set of rows tagged with that column's name. Done here with
  UNION ALL across the columns, the portable form of Snowflake's UNPIVOT.

  When to use it: when wide source data (one column per metric) needs to be
  normalised into a tidy long format for generic aggregation, charting, or
  storage in a tall key/value table. Long form lets you add new metrics without
  schema changes and is the natural input to GROUP BY across metrics.
*/
{{ config(materialized='view') }}

WITH wide_metrics AS (
    SELECT
        VISIT_ID,
        TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) AS visit_duration_secs,
        TRY_CAST(VISIT_PAGE_VIEWS AS NUMBER(38, 0)) AS visit_page_views
    FROM {{ source('studios_piano', 'studios_piano_events') }}
)

-- Fold each metric column into a (visit, metric_name, metric_value) row
SELECT
    VISIT_ID,
    'visit_duration_secs' AS metric_name,
    visit_duration_secs AS metric_value
FROM wide_metrics
UNION ALL
SELECT
    VISIT_ID,
    'visit_page_views' AS metric_name,
    visit_page_views AS metric_value
FROM wide_metrics
