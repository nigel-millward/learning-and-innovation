/*
  Technique: Projection Pushdown
  --------------------------------
  Select only the columns the model actually needs instead of SELECT *.
  Snowflake stores data column-by-column inside each micro-partition, so an
  explicit column list lets it read only those columns from storage and skip
  the rest entirely.

  Why it is useful: the source studios_piano_events table is very wide (several
  hundred columns). Reading 6 columns instead of all of them dramatically
  reduces the bytes scanned, the spill to local/remote disk, and the credits
  consumed — with no change to the result for downstream consumers that only
  need these fields.
*/
{{ config(materialized='view') }}

-- Optimised line: explicit projection (not SELECT *) so only these columns are read from storage
SELECT
    EVENT_ID,
    EVENT_TIME_UTC,
    VISITOR_ID,
    DEVICE_TYPE,
    GEO_COUNTRY,
    EVENT_NAME
FROM {{ source('studios_piano', 'studios_piano_events') }}
