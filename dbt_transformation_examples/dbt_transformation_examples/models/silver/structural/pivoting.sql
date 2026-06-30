/*
  Transformation: Pivoting (long -> wide)
  ---------------------------------------
  Pivoting turns row values into columns: each distinct value of a category
  becomes its own column, with an aggregate filling the cell. It reshapes a
  "long" table (one row per category) into a "wide" one (one row per entity,
  one column per category). Done here with conditional aggregation
  (SUM(CASE WHEN ...)), the portable form of Snowflake's PIVOT.

  When to use it: when a consumer needs categories side-by-side rather than
  stacked — e.g. a per-visitor row with one event-count column per device type,
  ready for a spreadsheet or a feature matrix. Pivot only on a small, known set
  of categories; an unbounded category set explodes the column count.
*/
{{ config(materialized='view') }}

SELECT
    VISITOR_ID,
    -- Conditional aggregation: one output column per known device type
    COUNT(CASE WHEN DEVICE_TYPE = 'desktop' THEN EVENT_ID END) AS desktop_events,
    COUNT(CASE WHEN DEVICE_TYPE = 'mobile' THEN EVENT_ID END) AS mobile_events,
    COUNT(CASE WHEN DEVICE_TYPE = 'tablet' THEN EVENT_ID END) AS tablet_events,
    COUNT(CASE WHEN DEVICE_TYPE = 'tv' THEN EVENT_ID END) AS tv_events
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY VISITOR_ID
