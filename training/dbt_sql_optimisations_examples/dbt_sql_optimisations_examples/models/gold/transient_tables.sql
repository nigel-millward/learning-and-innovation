/*
  Technique: Transient Tables (drop Fail-safe storage cost)
  ---------------------------------------------------------
  Materialise a table as TRANSIENT so it carries no 7-day Fail-safe period and
  only a minimal (or zero) Time Travel window. Snowflake therefore stops
  retaining historical micro-partitions for disaster recovery on this object.

  Why it is useful: every standard (permanent) table silently pays for up to 7
  days of Fail-safe storage on top of its live data plus its Time Travel
  retention — storage you cannot query and cannot switch off. For derived,
  reproducible data (gold aggregates, intermediate or training tables) that can
  simply be rebuilt from source, that recovery storage is wasted spend. Marking
  the model transient removes the Fail-safe cost while leaving the table fully
  usable. Reserve permanent tables for data that is NOT trivially reproducible.
*/
-- Optimised line: +transient=true builds a TRANSIENT table with no Fail-safe storage for this reproducible aggregate
{{ config(
    materialized='table',
    transient=true
) }}

SELECT
    DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
    SITE_ID,
    DEVICE_TYPE,
    COUNT(*) AS event_count,
    COUNT(DISTINCT VISITOR_ID) AS visitor_count
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY
    DATE_TRUNC('DAY', EVENT_TIME_UTC),
    SITE_ID,
    DEVICE_TYPE
