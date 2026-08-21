/*
  Transformation: Grouped Aggregations (GROUP BY summaries)
  ---------------------------------------------------------
  Grouped aggregation collapses many rows into one row per group, applying
  aggregate functions (COUNT, SUM, AVG, MIN/MAX, COUNT DISTINCT) within each
  group defined by GROUP BY. It reduces grain: from one row per event to one row
  per day/dimension.

  When to use it: to produce the summary tables that gold layers exist for —
  daily metrics by site, device, or country. This is the canonical
  fact-to-report transformation; HAVING filters the groups after aggregation
  when you need only groups meeting a threshold.
*/
{{ config(materialized='table') }}

SELECT
    DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
    SITE_ID,
    DEVICE_TYPE,
    COUNT(*) AS event_count,
    COUNT(DISTINCT VISITOR_ID) AS unique_visitors,
    COUNT(DISTINCT VISIT_ID) AS unique_visits,
    AVG(TRY_CAST(VISIT_DURATION AS NUMBER(38, 0))) AS avg_visit_duration_secs
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY
    DATE_TRUNC('DAY', EVENT_TIME_UTC),
    SITE_ID,
    DEVICE_TYPE
