/*
  Transformation: Date/Time Extraction
  -------------------------------------
  Date/time extraction pulls calendar parts out of a timestamp (year, month,
  day, hour, day-of-week) and computes intervals between timestamps with
  DATEDIFF / DATEADD. It converts a single instant into the analytic dimensions
  and durations that reporting needs.

  When to use it: whenever events carry a timestamp and you want to group by
  calendar grain, label rows by weekday, or measure elapsed time. These derived
  parts feed the time-series group later; deriving them once at silver keeps
  date logic consistent across every downstream model.
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    EVENT_TIME_UTC,
    -- DATE_TRUNC / DATE_PART pull calendar grains out of one instant
    DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
    DATE_PART('YEAR', EVENT_TIME_UTC) AS event_year,
    DATE_PART('HOUR', EVENT_TIME_UTC) AS event_hour,
    DAYNAME(EVENT_TIME_UTC) AS event_weekday,
    -- DATEDIFF measures an interval between two instants
    DATEDIFF('DAY', EVENT_TIME_UTC, CURRENT_DATE()) AS days_since_event
FROM {{ source('studios_piano', 'studios_piano_events') }}
