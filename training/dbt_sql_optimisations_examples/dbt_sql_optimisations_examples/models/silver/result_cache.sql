/*
  Technique: Result Cache Exploitation (deterministic SQL)
  --------------------------------------------------------
  Snowflake keeps the result of a query in a free, account-wide result cache for
  24 hours. If the exact same query is run again against unchanged data, the
  result is returned from cache for almost no time and zero warehouse credits.

  Why it is useful: the cache is only reused when the query is deterministic.
  Non-deterministic functions such as CURRENT_TIMESTAMP(), CURRENT_DATE(),
  RANDOM() or UUID_STRING() make every run look different, so Snowflake re-runs
  the whole query and the cache never helps. Designing models without those
  functions — e.g. deriving "today" from a stable column instead of
  CURRENT_DATE() — keeps repeat reads cacheable. Note the contrast with
  predicate_pushdown, which intentionally uses CURRENT_DATE() for a moving
  window; here we deliberately avoid it.
*/
{{ config(materialized='view') }}

-- Optimised line: only deterministic expressions (no CURRENT_DATE/TIMESTAMP/RANDOM) so repeat runs hit the result cache
SELECT
    SITE_ID,
    DEVICE_TYPE,
    GEO_COUNTRY,
    DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
    COUNT(*) AS event_count,
    COUNT(DISTINCT VISITOR_ID) AS visitor_count
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY
    SITE_ID,
    DEVICE_TYPE,
    GEO_COUNTRY,
    DATE_TRUNC('DAY', EVENT_TIME_UTC)
