/*
  Transformation: Horizontal Joins (combine tables side-by-side on a key)
  -----------------------------------------------------------------------
  A join matches rows from two inputs on a key and stitches their columns
  together, widening each row. The join type sets what happens to non-matches:
  INNER keeps only matches; LEFT keeps all left rows; FULL keeps both sides;
  CROSS pairs every row with every row; SEMI/ANTI (via EXISTS / NOT EXISTS) keep
  left rows that do / do not have a match without adding columns.

  When to use it: whenever an entity's attributes live in more than one place
  and must be assembled — events with the per-visitor first-touch context here.
  Choose the type by what you must preserve: LEFT to keep all events even when
  context is missing, SEMI/ANTI to filter by existence without fanning out rows.
*/
{{ config(materialized='table') }}

WITH events AS (
    SELECT
        EVENT_ID,
        EVENT_TIME_UTC,
        VISITOR_ID,
        SITE_ID
    FROM {{ source('studios_piano', 'studios_piano_events') }}
),

visitor_first_touch AS (
    SELECT
        VISITOR_ID,
        MIN(EVENT_TIME_UTC) AS first_seen,
        COUNT(*) AS lifetime_events
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    GROUP BY VISITOR_ID
)

-- LEFT JOIN keeps every event even if the visitor aggregate is somehow absent
SELECT
    e.EVENT_ID,
    e.EVENT_TIME_UTC,
    e.VISITOR_ID,
    e.SITE_ID,
    v.first_seen,
    v.lifetime_events
FROM events AS e
LEFT JOIN visitor_first_touch AS v
    ON e.VISITOR_ID = v.VISITOR_ID
