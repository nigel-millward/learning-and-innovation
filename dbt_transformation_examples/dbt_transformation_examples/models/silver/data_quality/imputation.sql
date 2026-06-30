/*
  Transformation: Imputation (fill missing numerics with a computed value)
  ------------------------------------------------------------------------
  Imputation replaces missing numeric values with an estimate derived from the
  data itself — a mean, median, or a carried-forward neighbour — rather than a
  flat literal. It keeps the row but substitutes a statistically reasonable
  value so the gap does not distort models that cannot tolerate NULLs.

  When to use it: when a measure feeds a calculation or ML feature that needs a
  number in every row and dropping the row would bias the result. Here a missing
  visit duration is filled with the group mean (per device type) via a window
  AVG, and a forward-fill alternative is shown. Always flag imputed rows so the
  estimate is not mistaken for observed data.
*/
{{ config(materialized='view') }}

SELECT
    VISIT_ID,
    DEVICE_TYPE,
    TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) AS visit_duration_secs,
    -- Mean imputation: fill missing duration with the per-device average
    COALESCE(
        TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)),
        ROUND(AVG(TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)))
            OVER (PARTITION BY DEVICE_TYPE))
    ) AS visit_duration_imputed,
    -- Flag so consumers can distinguish observed from imputed values
    (TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) IS NULL) AS is_imputed
FROM {{ source('studios_piano', 'studios_piano_events') }}
