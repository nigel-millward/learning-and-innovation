/*
  Technique: Incremental Models
  -----------------------------
  Materialise as 'incremental' so dbt builds the table once and afterwards only
  processes new/changed source rows, merging them into the existing table
  instead of rebuilding it from scratch every run.

  Why it is useful: rebuilding a large gold aggregate daily re-scans the entire
  history for no reason. With an incremental model the is_incremental() branch
  restricts the source scan to rows newer than what is already loaded, so each
  run reads and writes only the delta. This is the same "filter early" idea as
  predicate pushdown, applied across runs: the first CTE narrows to the new
  slice, and the downstream CTEs transform only that slice.
*/
{{ config(
    materialized='incremental',
    unique_key='event_day_site',
    incremental_strategy='merge'
) }}

WITH new_events AS (
    SELECT
        EVENT_ID,
        EVENT_TIME_UTC,
        VISITOR_ID,
        SITE_ID,
        DEVICE_TYPE
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    {% if is_incremental() %}
    -- Optimised line: only scan source rows newer than what is already loaded, so each run processes just the delta
    WHERE EVENT_TIME_UTC > (SELECT MAX(last_event_time_utc) FROM {{ this }})
    {% endif %}
),

daily_site_agg AS (
    SELECT
        DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
        SITE_ID,
        COUNT(*) AS event_count,
        COUNT(DISTINCT VISITOR_ID) AS visitor_count,
        MAX(EVENT_TIME_UTC) AS last_event_time_utc
    FROM new_events
    GROUP BY DATE_TRUNC('DAY', EVENT_TIME_UTC), SITE_ID
)

SELECT
    event_day || '|' || SITE_ID AS event_day_site,
    event_day,
    SITE_ID,
    event_count,
    visitor_count,
    last_event_time_utc
FROM daily_site_agg
