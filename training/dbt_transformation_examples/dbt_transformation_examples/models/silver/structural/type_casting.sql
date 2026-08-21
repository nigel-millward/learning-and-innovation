/*
  Transformation: Type Casting (explicit CAST / TRY_CAST)
  -------------------------------------------------------
  Type casting converts a value from one data type to another. CAST (or the ::
  operator) is strict and errors on a bad value; TRY_CAST returns NULL instead
  of failing. Casting fixes columns that arrive as the wrong type — numbers and
  timestamps stored as strings being the classic case.

  When to use it: at the silver layer when source columns are loosely typed
  (everything-as-VARCHAR landings are common in bronze). Prefer TRY_CAST for
  dirty free-text inputs so one malformed row does not abort the whole model,
  and reserve strict CAST for columns you trust to always be convertible.
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    -- Strict cast: we trust the source timestamp is always well-formed
    CAST(EVENT_TIME_UTC AS TIMESTAMP_NTZ) AS event_timestamp,
    -- Safe cast: free-text numeric fields may contain junk, so coerce to NULL
    TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) AS visit_duration_secs,
    TRY_CAST(VISIT_PAGE_VIEWS AS NUMBER(38, 0)) AS visit_page_views,
    CAST(SITE_ID AS STRING) AS site_id
FROM {{ source('studios_piano', 'studios_piano_events') }}
