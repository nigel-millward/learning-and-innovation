/*
  Transformation: Time-Zone Normalisation
  ----------------------------------------
  Time-zone normalisation converts timestamps recorded in different local zones
  to one canonical zone (almost always UTC) so they are directly comparable and
  orderable. CONVERT_TIMEZONE shifts an instant between named zones; from a
  UTC baseline it can also derive a local wall-clock time for display.

  When to use it: as early as possible whenever timestamps may originate in
  multiple zones — storing and computing in UTC avoids ordering bugs and
  double-counting around DST changes. Convert back to a local zone only at the
  presentation edge, never for storage or joins.
*/
{{ config(materialized='table') }}

SELECT
    EVENT_ID,
    EVENT_TIME_UTC,
    -- Canonical UTC instant, normalised from the stored timestamp
    CONVERT_TIMEZONE('UTC', EVENT_TIME_UTC) AS event_time_utc_norm,
    -- Local wall-clock derived from UTC for presentation only
    CONVERT_TIMEZONE('UTC', 'Europe/London', EVENT_TIME_UTC) AS event_time_london
FROM {{ source('studios_piano', 'studios_piano_events') }}
