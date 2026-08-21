/*
  Transformation: Global Aggregations (dataset-wide summary)
  ----------------------------------------------------------
  A global aggregation has no GROUP BY: it collapses the entire input to a
  single summary row. The same aggregate functions apply, but across all rows at
  once, producing dataset-wide totals and extremes.

  When to use it: for headline KPIs and data-profiling — total events, distinct
  visitors, the earliest and latest timestamp in the table. Useful as a
  one-row scorecard, or as a building block whose single value is later
  broadcast across rows (e.g. a grand total for share-of-total calculations).
*/
{{ config(materialized='table') }}

SELECT
    COUNT(*) AS total_events,
    COUNT(DISTINCT VISITOR_ID) AS total_visitors,
    COUNT(DISTINCT VISIT_ID) AS total_visits,
    COUNT(DISTINCT SITE_ID) AS total_sites,
    MIN(EVENT_TIME_UTC) AS earliest_event,
    MAX(EVENT_TIME_UTC) AS latest_event
FROM {{ source('studios_piano', 'studios_piano_events') }}
