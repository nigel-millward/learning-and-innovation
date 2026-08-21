/*
  Transformation: Normalization & Scaling (min-max, z-score)
  ----------------------------------------------------------
  Scaling rewrites a numeric measure onto a common range so features of
  different magnitudes are comparable. Min-max scaling maps values to [0, 1]
  using the column min and max; z-score (standardisation) centres on the mean
  and divides by the standard deviation, expressing each value as standard
  deviations from the mean.

  When to use it: as a preprocessing step for distance-based models, clustering,
  or any comparison where raw units would let a large-magnitude feature dominate.
  Window aggregates compute the column statistics once and broadcast them across
  every row; NULLIF guards a zero spread.
*/
{{ config(materialized='table') }}

WITH measures AS (
    SELECT
        VISIT_ID,
        TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) AS visit_duration_secs
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    WHERE TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) IS NOT NULL
)

SELECT
    VISIT_ID,
    visit_duration_secs,
    -- Min-max scaling to [0, 1]
    (visit_duration_secs - MIN(visit_duration_secs) OVER ())
    / NULLIF(
        MAX(visit_duration_secs) OVER () - MIN(visit_duration_secs) OVER (),
        0
    ) AS duration_minmax,
    -- Z-score standardisation
    (visit_duration_secs - AVG(visit_duration_secs) OVER ())
    / NULLIF(STDDEV(visit_duration_secs) OVER (), 0) AS duration_zscore
FROM measures
