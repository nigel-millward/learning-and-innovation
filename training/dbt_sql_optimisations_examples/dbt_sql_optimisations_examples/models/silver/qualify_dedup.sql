/*
  Technique: QUALIFY Window Deduplication
  ----------------------------------------
  Deduplicate rows by ranking them with a window function and filtering on the
  rank in a single QUALIFY clause. QUALIFY filters on the result of a window
  function the same way WHERE filters on columns and HAVING filters on
  aggregates.

  Why it is useful: the usual dedup pattern wraps the ROW_NUMBER() in a subquery
  or CTE and then adds a secondary `WHERE rn = 1` over that result — a second
  pass over the materialised intermediate. QUALIFY evaluates the window function
  and the keep-condition in the same scan, so it avoids that extra
  WHERE-clause pass and keeps the plan to a single, simpler step.
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    EVENT_TIME_UTC,
    VISITOR_ID,
    SITE_ID,
    EVENT_NAME
FROM {{ source('studios_piano', 'studios_piano_events') }}
-- Optimised line: QUALIFY keeps the latest row per EVENT_ID in one pass, avoiding a secondary WHERE rn = 1 scan
QUALIFY ROW_NUMBER() OVER (PARTITION BY EVENT_ID ORDER BY EVENT_TIME_UTC DESC) = 1
