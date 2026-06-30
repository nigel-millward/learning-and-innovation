/*
  Transformation: Conditional Logic (CASE / IFF / DECODE)
  -------------------------------------------------------
  Conditional logic derives a new value per row by branching on the row's other
  values. CASE WHEN is the general form; IFF is the two-branch shorthand; DECODE
  maps a column against a list of match/result pairs. All produce one derived
  column without changing the row count.

  When to use it: to bucket, classify, or flag rows — turning a raw measure into
  a band, or several boolean conditions into a single status label. It is the
  building block for the data-quality and binning transformations later in this
  tutorial.
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    VISITOR_ID,
    TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) AS visit_duration_secs,
    -- CASE: multi-branch banding of a numeric measure
    CASE
        WHEN TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) >= 600 THEN 'long'
        WHEN TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) >= 60 THEN 'medium'
        WHEN TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) IS NOT NULL THEN 'short'
        ELSE 'unknown'
    END AS visit_length_band,
    -- IFF: two-branch shorthand for a boolean flag
    IFF(DEVICE_TYPE = 'mobile', TRUE, FALSE) AS is_mobile
FROM {{ source('studios_piano', 'studios_piano_events') }}
