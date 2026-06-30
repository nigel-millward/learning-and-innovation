/*
  Technique: Clustering Keys
  --------------------------
  Define a clustering key on a large materialised table so Snowflake co-locates
  rows with similar key values in the same micro-partitions. Queries that filter
  or range-scan on the clustering key then prune far more partitions.

  Why it is useful: this daily aggregate is materialised as a table and read
  repeatedly with filters on date and site. Clustering by (EVENT_DAY, SITE_ID)
  keeps each day/site contiguous, so a query for one day touches a handful of
  micro-partitions instead of the whole table. The benefit shows on READ, not on
  the build, and is worth it only for large, frequently-filtered tables — over-
  clustering a small or rarely-filtered table just adds reclustering cost.
*/
{{ config(
    materialized='table',
    cluster_by=['EVENT_DAY', 'SITE_ID']
) }}
-- Optimised line above: cluster_by co-locates rows by EVENT_DAY/SITE_ID so reads prune more micro-partitions

SELECT
    DATE_TRUNC('DAY', EVENT_TIME_UTC) AS EVENT_DAY,
    SITE_ID,
    DEVICE_TYPE,
    GEO_COUNTRY,
    COUNT(*) AS event_count,
    COUNT(DISTINCT VISITOR_ID) AS visitor_count
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY
    DATE_TRUNC('DAY', EVENT_TIME_UTC),
    SITE_ID,
    DEVICE_TYPE,
    GEO_COUNTRY
