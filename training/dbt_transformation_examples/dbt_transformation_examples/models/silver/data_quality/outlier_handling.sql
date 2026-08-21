/*
  Transformation: Outlier Handling (cap / clip / remove extremes)
  ---------------------------------------------------------------
  Outlier handling limits the influence of extreme values. Two strategies:
  capping (winsorising) replaces values beyond a threshold with the threshold
  itself, keeping the row; removal filters the row out entirely. Thresholds come
  from percentiles or a fixed business bound.

  When to use it: when a few absurd measures (a multi-day "visit", a negative
  duration) would dominate an average or break a scale. Capping preserves the
  row and its other columns while taming the value; removal is for values that
  are clearly invalid rather than merely extreme.
*/
{{ config(materialized='view') }}

WITH bounds AS (
    -- Robust upper bound from a high percentile, computed once over the data
    SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (
        ORDER BY TRY_CAST(VISIT_DURATION AS NUMBER(38, 0))
    ) AS p99_duration
    FROM {{ source('studios_piano', 'studios_piano_events') }}
)

SELECT
    e.VISIT_ID,
    TRY_CAST(e.VISIT_DURATION AS NUMBER(38, 0)) AS visit_duration_secs,
    -- Cap (winsorise) at the p99 bound; LEAST keeps the row but tames the value
    LEAST(
        TRY_CAST(e.VISIT_DURATION AS NUMBER(38, 0)),
        b.p99_duration
    ) AS visit_duration_capped
FROM {{ source('studios_piano', 'studios_piano_events') }} AS e
CROSS JOIN bounds AS b
-- Removal: drop values that are invalid (negative), not merely large
WHERE TRY_CAST(e.VISIT_DURATION AS NUMBER(38, 0)) >= 0
