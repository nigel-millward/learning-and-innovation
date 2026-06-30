/*
  Transformation: Discretization / Binning (continuous -> categorical)
  --------------------------------------------------------------------
  Binning converts a continuous measure into a small set of ordered categories.
  WIDTH_BUCKET assigns each value to an equal-width bin between a low and high
  bound; a CASE expression cuts custom (business-defined) breakpoints. Either
  way a numeric column becomes a labelled band.

  When to use it: to turn a measure into a dimension for reporting (duration ->
  short/medium/long), to reduce noise before modelling, or to satisfy algorithms
  that expect categorical inputs. Equal-width bins are quick; explicit CASE
  breakpoints encode domain knowledge about where the meaningful cut-offs lie.
*/
{{ config(materialized='table') }}

SELECT
    VISIT_ID,
    TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) AS visit_duration_secs,
    -- WIDTH_BUCKET: 5 equal-width bins between 0 and 3600 seconds
    WIDTH_BUCKET(
        TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)), 0, 3600, 5
    ) AS duration_bucket,
    -- CASE: custom business breakpoints with readable labels
    CASE
        WHEN TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) < 60 THEN 'under_1m'
        WHEN TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) < 300 THEN '1m_to_5m'
        WHEN TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) < 1800 THEN '5m_to_30m'
        ELSE 'over_30m'
    END AS duration_band
FROM {{ source('studios_piano', 'studios_piano_events') }}
