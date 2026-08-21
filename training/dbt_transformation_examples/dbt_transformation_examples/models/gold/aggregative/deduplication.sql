/*
  Transformation: Deduplication (one row per key)
  ------------------------------------------------
  Deduplication reduces a set of rows that share a key down to a single chosen
  representative. The idiomatic Snowflake form ranks rows within each key with
  ROW_NUMBER() and keeps rank 1 in a QUALIFY clause — picking, say, the latest
  row per key in one pass, with no secondary subquery scan.

  When to use it: whenever a key should be unique but the source carries
  duplicates or late-arriving restatements (re-sent events, slowly changing
  records). The ORDER BY inside the window decides which copy wins — here the
  most recent EVENT_TIME_UTC per EVENT_ID.
*/
{{ config(materialized='table') }}

SELECT
    EVENT_ID,
    EVENT_TIME_UTC,
    VISITOR_ID,
    SITE_ID,
    EVENT_NAME
FROM {{ source('studios_piano', 'studios_piano_events') }}
-- Keep only the latest row per EVENT_ID in a single pass
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY EVENT_ID ORDER BY EVENT_TIME_UTC DESC
) = 1
