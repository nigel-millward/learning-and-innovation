/*
  Transformation: Nesting / Structuring (rows -> complex column)
  --------------------------------------------------------------
  Nesting is the inverse of flattening: it collapses several columns or several
  rows into a single semi-structured value. OBJECT_CONSTRUCT builds a VARIANT
  object from key/value pairs in a row; ARRAY_AGG collects values across the
  rows of a group into an array. The result is one rich column instead of many
  flat ones.

  When to use it: when downstream consumers (an API, a document store, a JSON
  export) want a structured payload rather than a wide flat row, or when you
  want to carry a variable-length collection (all tags for a visitor) in one
  column without a separate child table.
*/
{{ config(materialized='view') }}

SELECT
    VISITOR_ID,
    -- ARRAY_AGG collapses many event rows into one array per visitor
    ARRAY_AGG(EVENT_ID) AS event_ids,
    -- OBJECT_CONSTRUCT packs row attributes into a single VARIANT object
    OBJECT_CONSTRUCT(
        'first_seen', MIN(EVENT_TIME_UTC),
        'last_seen', MAX(EVENT_TIME_UTC),
        'event_count', COUNT(*)
    ) AS visitor_summary
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY VISITOR_ID
