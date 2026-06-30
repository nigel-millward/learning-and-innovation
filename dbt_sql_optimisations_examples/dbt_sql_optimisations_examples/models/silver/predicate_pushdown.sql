/*
  Technique: Predicate Pushdown (filter early in a multi-CTE model)
  -----------------------------------------------------------------
  Apply a selective filter as early as possible and keep the filtered column
  "bare" (no function wrapped around it). Snowflake pushes the WHERE predicate
  down to the storage layer and uses micro-partition metadata to prune
  partitions that cannot match, so it never reads them.

  Why doing it in the FIRST CTE matters: in a long model the row count chosen by
  the first step flows through every CTE after it. If the date filter lives in
  the first CTE, the joins, window functions and aggregations downstream all run
  over ~30 days of data instead of the full history. If the same filter were
  left until the final WHERE, those intermediate steps would process the entire
  table first and only trim at the end — far more scanned bytes, spill and
  credits for an identical result. So: filter first, then build.

  The key rule is to avoid wrapping the filtered column in a function (e.g.
  YEAR(EVENT_TIME_UTC)), because that defeats pruning; compare against a
  literal/expression on the right-hand side instead.
*/
{{ config(materialized='view') }}

WITH filtered_events AS (
    -- FIRST CTE = the optimisation: prune to 30 days up front so every CTE below scans less
    SELECT
        EVENT_ID,
        EVENT_TIME_UTC,
        VISITOR_ID,
        SITE_ID,
        EVENT_NAME,
        DEVICE_TYPE,
        GEO_COUNTRY
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    -- Optimised line: bare column compared to a right-hand expression so Snowflake prunes micro-partitions
    WHERE EVENT_TIME_UTC >= DATEADD('DAY', -30, CURRENT_DATE())
),

visitor_sessions AS (
    -- Runs over the already-pruned 30-day set, not the full table
    SELECT
        VISITOR_ID,
        SITE_ID,
        DEVICE_TYPE,
        GEO_COUNTRY,
        COUNT(*) AS event_count,
        COUNT(DISTINCT EVENT_NAME) AS distinct_event_types,
        MIN(EVENT_TIME_UTC) AS first_event_time_utc,
        MAX(EVENT_TIME_UTC) AS last_event_time_utc
    FROM filtered_events
    GROUP BY VISITOR_ID, SITE_ID, DEVICE_TYPE, GEO_COUNTRY
),

session_durations AS (
    -- Also inherits the early filter; no need to re-filter here
    SELECT
        VISITOR_ID,
        SITE_ID,
        DEVICE_TYPE,
        GEO_COUNTRY,
        event_count,
        distinct_event_types,
        DATEDIFF('SECOND', first_event_time_utc, last_event_time_utc) AS session_seconds
    FROM visitor_sessions
)

SELECT
    VISITOR_ID,
    SITE_ID,
    DEVICE_TYPE,
    GEO_COUNTRY,
    event_count,
    distinct_event_types,
    session_seconds
FROM session_durations
