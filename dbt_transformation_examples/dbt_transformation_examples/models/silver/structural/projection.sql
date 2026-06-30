/*
  Transformation: Projection (select / drop / reorder columns)
  ------------------------------------------------------------
  Projection chooses *which columns* leave a model and in what order. It is the
  most basic structural transformation: an explicit SELECT list that keeps the
  columns you need, drops the ones you do not, and presents them in a stable
  order. The row count is unchanged — only the shape of each row changes.

  When to use it: almost always. Replacing SELECT * with an explicit list makes
  a model's output contract clear, stops downstream breakage when the source
  adds or reorders columns, and lets the warehouse read fewer columns. Reach for
  it as the first step of nearly every silver model.
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    EVENT_TIME_UTC,
    VISITOR_ID,
    VISIT_ID,
    SITE_ID,
    EVENT_NAME,
    DEVICE_TYPE,
    BROWSER,
    OS,
    GEO_COUNTRY
FROM {{ source('studios_piano', 'studios_piano_events') }}
