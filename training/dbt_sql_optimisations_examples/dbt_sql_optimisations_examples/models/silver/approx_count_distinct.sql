/*
  Technique: Approximate Aggregation (APPROX_COUNT_DISTINCT / HyperLogLog)
  -----------------------------------------------------------------------
  Replace an exact COUNT(DISTINCT high_cardinality_column) with
  APPROX_COUNT_DISTINCT, which uses the HyperLogLog algorithm to estimate the
  number of distinct values from a compact sketch rather than tracking every
  value seen.

  Why it is useful: an exact COUNT(DISTINCT VISITOR_ID) must hold every distinct
  key in memory to guarantee an exact answer, which spills to disk and burns
  credits once the cardinality is large. APPROX_COUNT_DISTINCT keeps only a
  small fixed-size sketch, so it runs far faster with much less memory and
  spill, at the cost of a small (~1-2%) error. For dashboards, trends and
  "roughly how many uniques?" questions that error is irrelevant, so the
  approximate form is the right default; reserve exact COUNT(DISTINCT) for
  figures that must reconcile precisely. The sibling APPROX_PERCENTILE does the
  same for percentiles.
*/
{{ config(materialized='view') }}

SELECT
    SITE_ID,
    DEVICE_TYPE,
    GEO_COUNTRY,
    DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
    COUNT(*) AS event_count,
    -- Optimised line: APPROX_COUNT_DISTINCT estimates uniques from a small sketch instead of tracking every key
    APPROX_COUNT_DISTINCT(VISITOR_ID) AS approx_visitor_count
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY
    SITE_ID,
    DEVICE_TYPE,
    GEO_COUNTRY,
    DATE_TRUNC('DAY', EVENT_TIME_UTC)
