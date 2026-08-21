/*
  Technique: Query Acceleration Service (QAS)
  -------------------------------------------
  QAS lets a warehouse automatically offload the large, "outlier" parts of a
  scan (big table scans, bursty filtering) onto shared Snowflake compute, so a
  modest warehouse can absorb an occasional huge query without being permanently
  oversized.

  Why it is useful: this kind of full-history aggregation is exactly the bursty,
  scan-heavy workload QAS targets. Rather than scaling the whole warehouse up for
  one heavy model, QAS borrows serverless compute just for the eligible scan
  portion and bills only for what it uses.

  QAS is a WAREHOUSE-level setting, not a model config, so it cannot be enabled
  from inside this SELECT. Enable it on the warehouse that runs this model with
  the reference statements below (requires suitable privileges):

    -- Optimised line (run once on the warehouse, not part of the model build):
    -- ALTER WAREHOUSE SDP_ETL_LG_WH SET
    --   ENABLE_QUERY_ACCELERATION = TRUE
    --   QUERY_ACCELERATION_MAX_SCALE_FACTOR = 8;
    -- Check eligibility first with SYSTEM$ESTIMATE_QUERY_ACCELERATION.
*/
{{ config(materialized='table') }}

SELECT
    SITE_ID,
    DEVICE_TYPE,
    GEO_COUNTRY,
    COUNT(*) AS event_count,
    COUNT(DISTINCT VISITOR_ID) AS visitor_count,
    MIN(EVENT_TIME_UTC) AS first_event_time_utc,
    MAX(EVENT_TIME_UTC) AS last_event_time_utc
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY
    SITE_ID,
    DEVICE_TYPE,
    GEO_COUNTRY
