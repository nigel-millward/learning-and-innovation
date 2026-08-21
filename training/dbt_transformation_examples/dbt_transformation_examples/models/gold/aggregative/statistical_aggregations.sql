/*
  Transformation: Statistical / Distribution Aggregations
  -------------------------------------------------------
  Beyond COUNT/SUM/AVG, aggregation can describe the *shape* of a measure within
  each group: central tendency that resists outliers (MEDIAN), spread (STDDEV,
  variance), arbitrary quantiles (PERCENTILE_CONT for the interpolated value,
  PERCENTILE_DISC for an actual observed value), the most common value (MODE),
  and cheap high-cardinality counts (APPROX_COUNT_DISTINCT / HLL).

  When to use it: when an average hides the story — a median session and the 90th
  percentile say far more about user experience than the mean, which a few long
  sessions can skew. Use APPROX_COUNT_DISTINCT when an exact distinct count is
  expensive and a small error is acceptable.
*/
{{ config(materialized='table') }}

SELECT
    SITE_ID,
    COUNT(*) AS event_count,
    -- Robust central tendency vs. the mean
    AVG(TRY_CAST(VISIT_DURATION AS NUMBER(38, 0))) AS mean_duration,
    MEDIAN(TRY_CAST(VISIT_DURATION AS NUMBER(38, 0))) AS median_duration,
    -- Spread of the distribution
    STDDEV(TRY_CAST(VISIT_DURATION AS NUMBER(38, 0))) AS stddev_duration,
    -- Interpolated 90th percentile (tail of the distribution)
    PERCENTILE_CONT(0.9) WITHIN GROUP (
        ORDER BY TRY_CAST(VISIT_DURATION AS NUMBER(38, 0))
    ) AS p90_duration,
    -- Most frequent device for the site
    MODE(DEVICE_TYPE) AS modal_device,
    -- Approximate distinct count: cheaper than exact at high cardinality
    APPROX_COUNT_DISTINCT(VISITOR_ID) AS approx_unique_visitors
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY SITE_ID
