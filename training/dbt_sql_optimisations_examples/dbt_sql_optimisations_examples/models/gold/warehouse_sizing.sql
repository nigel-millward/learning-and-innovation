/*
  Technique: Warehouse Sizing, Auto-Suspend & Multi-Cluster
  ---------------------------------------------------------
  Match the virtual warehouse to the workload instead of running one large,
  always-on warehouse for everything. The main levers are:
    - SIZE          : bigger = more compute per second but proportionally more
                      credits. Size up only until a query stops spilling; going
                      larger after that just costs more for no speed-up.
    - AUTO_SUSPEND  : suspend the warehouse after a short idle period so you stop
                      paying the moment work finishes (Snowflake bills per second
                      while a warehouse is running, idle or not).
    - AUTO_RESUME   : bring it back automatically on the next query so the saving
                      is invisible to callers.
    - MULTI-CLUSTER : add clusters for CONCURRENCY (many simultaneous queries),
                      not for a single big query — that is what sizing/QAS are for.
    - SEPARATE WAREHOUSES per workload (load vs transform vs BI) so a heavy job
      cannot starve another and each can be sized and suspended independently.

  Why it is useful: warehouse configuration is usually the single biggest lever
  on Snowflake spend — far larger than any one query rewrite. An oversized,
  never-suspending warehouse wastes credits continuously.

  This is a WAREHOUSE-level setting, not a model config, so it cannot be set from
  inside this SELECT. Configure the warehouse that runs this project with the
  reference statements below (requires suitable privileges):

    -- Optimised reference (run once on the warehouse, not part of the model build):
    -- ALTER WAREHOUSE SDP_ETL_LG_WH SET
    --   WAREHOUSE_SIZE = 'MEDIUM'
    --   AUTO_SUSPEND = 60          -- seconds idle before suspend
    --   AUTO_RESUME = TRUE
    --   MIN_CLUSTER_COUNT = 1
    --   MAX_CLUSTER_COUNT = 3      -- scale out for concurrency, not for one big query
    --   SCALING_POLICY = 'STANDARD';
*/
{{ config(materialized='table') }}

SELECT
    DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
    SITE_ID,
    COUNT(*) AS event_count
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY
    DATE_TRUNC('DAY', EVENT_TIME_UTC),
    SITE_ID
