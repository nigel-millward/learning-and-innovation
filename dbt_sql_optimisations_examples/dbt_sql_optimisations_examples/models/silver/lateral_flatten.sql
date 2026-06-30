/*
  Technique: LATERAL FLATTEN (unnest arrays instead of heavy joins)
  -----------------------------------------------------------------
  Use LATERAL FLATTEN to expand a VARIANT/ARRAY column into one row per element
  in a single pass, rather than self-joining the table to itself or running
  several joins to associate tags with events. FLATTEN streams the nested
  values out alongside their parent row, so the parent is read once.

  Why it is useful: the source carries event tags in the TAGS_ARRAY column.
  Without FLATTEN you would either explode the data with extra joins or post-
  process it elsewhere. FLATTEN keeps the work set-based and inside one scan of
  the (already projected) event rows, then lets you aggregate the unnested rows
  normally. This is the idiomatic, cheapest way to handle semi-structured data
  in Snowflake.
*/
{{ config(materialized='view') }}

WITH events AS (
    -- Narrow projection first so FLATTEN streams only what we need
    SELECT
        EVENT_ID,
        EVENT_TIME_UTC,
        VISITOR_ID,
        TAGS_ARRAY
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    WHERE TAGS_ARRAY IS NOT NULL
),

exploded_tags AS (
    SELECT
        e.EVENT_ID,
        e.EVENT_TIME_UTC,
        e.VISITOR_ID,
        tag.value::STRING AS tag_value
    FROM events AS e,
        -- Optimised line: LATERAL FLATTEN unnests TAGS_ARRAY in one pass instead of multiple heavy joins
        LATERAL FLATTEN(input => e.TAGS_ARRAY) AS tag
)

SELECT
    tag_value,
    COUNT(DISTINCT EVENT_ID) AS event_count,
    COUNT(DISTINCT VISITOR_ID) AS visitor_count
FROM exploded_tags
GROUP BY tag_value
