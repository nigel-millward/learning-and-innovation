/*
  Technique: Early Aggregation & Filtering (before joins)
  -------------------------------------------------------
  Filter and aggregate each input down to its smallest useful form in its own
  CTE *before* joining, rather than joining the raw tables and aggregating at
  the end. Joins are the expensive step; the less data that reaches them, the
  cheaper they are.

  Why it is useful: a naive query joins full event data to a per-site lookup and
  only then groups — the join processes every raw event row. Here each side is
  reduced first: events are filtered and pre-aggregated to one row per
  day/site, the site dimension is de-duplicated, and only those small results
  are joined. The join input shrinks from millions of event rows to one row per
  day/site, cutting join memory, spill and time for an identical result.
*/
{{ config(materialized='table') }}

WITH events_filtered AS (
    -- Filter early so nothing below processes more than 90 days
    SELECT
        EVENT_TIME_UTC,
        SITE_ID,
        VISITOR_ID
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    WHERE EVENT_TIME_UTC >= DATEADD('DAY', -90, CURRENT_DATE())
),

daily_site_metrics AS (
    -- Optimised line: pre-aggregate BEFORE the join so the join input is one row per day/site, not raw events
    SELECT
        DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
        SITE_ID,
        COUNT(*) AS event_count,
        COUNT(DISTINCT VISITOR_ID) AS visitor_count
    FROM events_filtered
    GROUP BY DATE_TRUNC('DAY', EVENT_TIME_UTC), SITE_ID
),

site_dim AS (
    -- Reduce the dimension to one row per site before joining
    SELECT DISTINCT
        SITE_ID,
        FIRST_VALUE(GEO_COUNTRY) OVER (
            PARTITION BY SITE_ID ORDER BY EVENT_TIME_UTC DESC
        ) AS latest_geo_country
    FROM {{ source('studios_piano', 'studios_piano_events') }}
)

SELECT
    m.event_day,
    m.SITE_ID,
    d.latest_geo_country,
    m.event_count,
    m.visitor_count
FROM daily_site_metrics AS m
INNER JOIN site_dim AS d
    ON m.SITE_ID = d.SITE_ID
