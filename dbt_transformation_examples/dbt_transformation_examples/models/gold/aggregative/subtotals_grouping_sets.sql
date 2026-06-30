/*
  Transformation: Subtotals (GROUPING SETS / ROLLUP / CUBE)
  ---------------------------------------------------------
  A normal GROUP BY produces one grain. GROUPING SETS, ROLLUP and CUBE compute
  several grains in a single pass and stack them: ROLLUP adds hierarchical
  subtotals (by day+site, then by day, then grand total); CUBE adds every
  combination of the dimensions; GROUPING SETS lets you name the exact grains you
  want. GROUPING() marks which rows are subtotals so they can be labelled or
  filtered.

  When to use it: to build a report that needs detail rows and their subtotals
  and grand total together — daily-by-site numbers plus the daily and overall
  rollups — without UNION-ing several separate aggregate queries. ROLLUP is the
  right tool when the dimensions form a natural hierarchy.
*/
{{ config(materialized='table') }}

SELECT
    DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
    SITE_ID,
    COUNT(*) AS event_count,
    COUNT(DISTINCT VISITOR_ID) AS unique_visitors,
    -- GROUPING() = 1 marks a row where this column was rolled up (a subtotal)
    GROUPING(SITE_ID) AS is_site_subtotal,
    GROUPING(DATE_TRUNC('DAY', EVENT_TIME_UTC)) AS is_day_subtotal
FROM {{ source('studios_piano', 'studios_piano_events') }}
-- ROLLUP yields (day, site), (day), and () grand-total grains in one pass
GROUP BY ROLLUP (DATE_TRUNC('DAY', EVENT_TIME_UTC), SITE_ID)
