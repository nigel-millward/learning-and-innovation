/*
  Technique: UNION ALL instead of UNION
  --------------------------------------
  Use UNION ALL to concatenate two result sets when you already know they do not
  overlap (or duplicates are acceptable), rather than UNION.

  Why it is useful: UNION implicitly de-duplicates the combined result, which
  forces Snowflake to sort/hash every row across both inputs to find and drop
  duplicates — an expensive, memory-hungry step that can spill on large sets.
  UNION ALL skips that step entirely and simply streams both inputs through. When
  the branches are disjoint by construction (here, two non-overlapping event-name
  groups), the de-duplication can never remove a row, so UNION would pay the full
  sort cost for an identical result. Only reach for plain UNION when duplicates
  genuinely can occur AND must be removed.
*/
{{ config(materialized='view') }}

WITH page_views AS (
    SELECT
        EVENT_ID,
        EVENT_TIME_UTC,
        VISITOR_ID,
        SITE_ID,
        'PAGE_VIEW' AS event_group
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    WHERE EVENT_NAME = 'page_view'
),

conversions AS (
    SELECT
        EVENT_ID,
        EVENT_TIME_UTC,
        VISITOR_ID,
        SITE_ID,
        'CONVERSION' AS event_group
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    WHERE EVENT_NAME = 'conversion'
)

SELECT * FROM page_views
-- Optimised line: UNION ALL skips the de-dup sort because these two branches are disjoint by construction
UNION ALL
SELECT * FROM conversions
