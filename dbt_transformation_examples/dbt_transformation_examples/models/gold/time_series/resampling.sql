/*
  Transformation: Resampling (change time frequency)
  --------------------------------------------------
  Resampling changes the time grain of event data. Downsampling rolls fine-
  grained events up to a coarser bucket (events -> hourly or daily counts) with
  DATE_TRUNC + GROUP BY. Upsampling goes the other way, generating a row per
  period so that gaps become explicit zero rows rather than missing dates.

  When to use it: to put irregular event streams onto a regular calendar grid —
  the prerequisite for any time-series chart, moving average, or
  period-over-period comparison. Downsampling here truncates to the hour and
  aggregates; a date spine (generated series) would fill empty periods for true
  upsampling.
*/
{{ config(materialized='table') }}

SELECT
    -- DATE_TRUNC downsamples events to a regular hourly grid
    DATE_TRUNC('HOUR', EVENT_TIME_UTC) AS event_hour,
    SITE_ID,
    COUNT(*) AS event_count,
    COUNT(DISTINCT VISITOR_ID) AS unique_visitors
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY
    DATE_TRUNC('HOUR', EVENT_TIME_UTC),
    SITE_ID
