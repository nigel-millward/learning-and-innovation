/*
  Transformation: Categorical Encoding (one-hot, label / ordinal)
  ---------------------------------------------------------------
  Encoding turns a categorical column into numbers a model can consume. One-hot
  encoding creates a 0/1 indicator column per category (no false ordering
  implied). Label / ordinal encoding maps each category to an integer — valid
  only when the categories have a genuine order.

  When to use it: to prepare categorical features for ML or numeric analysis.
  Use one-hot for nominal categories with a small, known set of values (a large
  set explodes the column count); use ordinal encoding only when the integer
  order is meaningful (e.g. small < medium < large).
*/
{{ config(materialized='table') }}

SELECT
    EVENT_ID,
    DEVICE_TYPE,
    -- One-hot: one indicator column per nominal category
    IFF(DEVICE_TYPE = 'desktop', 1, 0) AS is_desktop,
    IFF(DEVICE_TYPE = 'mobile', 1, 0) AS is_mobile,
    IFF(DEVICE_TYPE = 'tablet', 1, 0) AS is_tablet,
    IFF(DEVICE_TYPE = 'tv', 1, 0) AS is_tv,
    -- Ordinal: integer code where the order is meaningful (screen size)
    CASE DEVICE_TYPE
        WHEN 'mobile' THEN 1
        WHEN 'tablet' THEN 2
        WHEN 'desktop' THEN 3
        WHEN 'tv' THEN 4
        ELSE 0
    END AS device_size_rank
FROM {{ source('studios_piano', 'studios_piano_events') }}
