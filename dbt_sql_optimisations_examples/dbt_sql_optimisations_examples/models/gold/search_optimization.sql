/*
  Technique: Search Optimization Service (SOS)
  --------------------------------------------
  Add the Search Optimization Service to a large table to accelerate highly
  selective point-lookups (equality / IN predicates on high-cardinality
  columns) without changing the clustering key. SOS maintains a separate search
  access path that lets Snowflake jump to the matching micro-partitions.

  Why it is useful: clustering helps range scans on the cluster key, but ad-hoc
  point-lookups on a *different* high-cardinality column (e.g. find every event
  for one VISITOR_ID) still scan widely. SOS targets exactly that pattern. It is
  applied as a post-hook after the table is built — see the optimised line in
  the config below.

  Note: SOS requires Snowflake Enterprise Edition and ADD SEARCH OPTIMIZATION
  privileges. If the training role lacks them, comment out the post_hook; the
  model still builds.
*/
{{ config(
    materialized='table',
    cluster_by=['EVENT_DAY'],
    post_hook="ALTER TABLE {{ this }} ADD SEARCH OPTIMIZATION ON EQUALITY(VISITOR_ID)"
) }}
-- Optimised line above: post_hook adds SOS for fast point-lookups on VISITOR_ID, independent of the cluster key

SELECT
    DATE_TRUNC('DAY', EVENT_TIME_UTC) AS EVENT_DAY,
    VISITOR_ID,
    SITE_ID,
    COUNT(*) AS event_count,
    MAX(EVENT_TIME_UTC) AS last_event_time_utc
FROM {{ source('studios_piano', 'studios_piano_events') }}
GROUP BY
    DATE_TRUNC('DAY', EVENT_TIME_UTC),
    VISITOR_ID,
    SITE_ID
