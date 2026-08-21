/*
  Transformation: Filtering (row selection)
  -----------------------------------------
  Filtering keeps or discards whole rows based on a boolean condition in a WHERE
  clause. It changes the row count, never the columns. It is the workhorse for
  scoping a model to the rows that matter: a date window, a status, a non-null
  key.

  When to use it: in nearly every model, and as early as possible. Filtering in
  the first CTE (predicate pushdown) shrinks everything downstream and lets
  Snowflake prune micro-partitions, so a tight WHERE is both a correctness tool
  and the cheapest performance win available.
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    EVENT_TIME_UTC,
    VISITOR_ID,
    SITE_ID,
    EVENT_NAME
FROM {{ source('studios_piano', 'studios_piano_events') }}
-- Keep only recent, well-keyed rows from the sites we care about
WHERE EVENT_TIME_UTC >= DATEADD('DAY', -30, CURRENT_DATE())
    AND EVENT_ID IS NOT NULL
    AND SITE_ID IS NOT NULL
