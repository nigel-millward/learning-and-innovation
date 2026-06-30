/*
  Transformation: Mathematical Scaling (variance-stabilising transforms)
  ----------------------------------------------------------------------
  Mathematical scaling applies a non-linear function — log, square root,
  exponential — to compress or stretch a measure's distribution. A log transform
  pulls in a long right tail so a heavily skewed measure becomes roughly
  symmetric; sqrt is a milder version; exp reverses a log.

  When to use it: when a measure spans many orders of magnitude and its skew
  would distort averages, correlations, or model fits. Use LN(x + 1) (log1p) so
  that zero maps to zero and the function is defined at the origin; guard against
  negatives, which a log cannot take.
*/
{{ config(materialized='table') }}

SELECT
    VISIT_ID,
    TRY_CAST(VISIT_PAGE_VIEWS AS NUMBER(38, 0)) AS visit_page_views,
    -- log1p: LN(x + 1) compresses a long right tail, maps 0 -> 0
    LN(GREATEST(TRY_CAST(VISIT_PAGE_VIEWS AS NUMBER(38, 0)), 0) + 1)
        AS page_views_log1p,
    -- sqrt: milder variance-stabilising transform
    SQRT(GREATEST(TRY_CAST(VISIT_PAGE_VIEWS AS NUMBER(38, 0)), 0))
        AS page_views_sqrt
FROM {{ source('studios_piano', 'studios_piano_events') }}
