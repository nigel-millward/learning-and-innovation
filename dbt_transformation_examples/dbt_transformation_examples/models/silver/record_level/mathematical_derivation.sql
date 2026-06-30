/*
  Transformation: Mathematical Derivation (arithmetic across columns)
  -------------------------------------------------------------------
  Mathematical derivation computes a new measure from arithmetic on a row's
  existing columns: ratios, rates, differences, products. The calculation is
  row-local — it never reaches across rows (that is aggregation, a later group).

  When to use it: to turn raw measures into the analytic quantity a consumer
  actually wants — pages-per-minute from page views and duration, a price net of
  discount, a percentage. Guard divisions with NULLIF so a zero denominator
  yields NULL instead of erroring the whole query.
*/
{{ config(materialized='view') }}

SELECT
    VISIT_ID,
    TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)) AS visit_duration_secs,
    TRY_CAST(VISIT_PAGE_VIEWS AS NUMBER(38, 0)) AS visit_page_views,
    -- Ratio with NULLIF guard so a zero duration gives NULL, not an error
    ROUND(
        TRY_CAST(VISIT_PAGE_VIEWS AS NUMBER(38, 0))
        / NULLIF(TRY_CAST(VISIT_DURATION AS NUMBER(38, 0)), 0) * 60,
        2
    ) AS page_views_per_minute
FROM {{ source('studios_piano', 'studios_piano_events') }}
