/*
  Transformation: Sessionisation (gap-and-islands)
  ------------------------------------------------
  Sessionisation groups a stream of timestamped events per entity into bounded
  "sessions": a run of activity broken whenever the gap to the previous event
  exceeds an inactivity threshold. This is the classic gap-and-islands pattern —
  LAG finds the gap to the prior event, a boolean flags each new session start,
  and a running SUM of those flags numbers the sessions within each visitor.

  When to use it: to turn a raw clickstream into analysable visits — counting
  sessions, measuring session length, or attributing events to the visit that
  contained them — when the source has no reliable session key of its own. The
  30-minute threshold here is the common web-analytics convention; adjust per
  domain.
*/
{{ config(materialized='table') }}

WITH ordered AS (
    SELECT
        EVENT_ID,
        VISITOR_ID,
        EVENT_TIME_UTC,
        -- Seconds since this visitor's previous event (NULL for their first)
        DATEDIFF(
            'SECOND',
            LAG(EVENT_TIME_UTC) OVER (
                PARTITION BY VISITOR_ID ORDER BY EVENT_TIME_UTC
            ),
            EVENT_TIME_UTC
        ) AS secs_since_prev
    FROM {{ source('studios_piano', 'studios_piano_events') }}
),

flagged AS (
    SELECT
        *,
        -- New session when the gap exceeds 30 min, or on the visitor's first event
        IFF(
            secs_since_prev IS NULL OR secs_since_prev > 1800, 1, 0
        ) AS is_session_start
    FROM ordered
)

SELECT
    EVENT_ID,
    VISITOR_ID,
    EVENT_TIME_UTC,
    -- Running sum of session-start flags numbers sessions within the visitor
    SUM(is_session_start) OVER (
        PARTITION BY VISITOR_ID
        ORDER BY EVENT_TIME_UTC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS session_seq,
    -- A stable surrogate session key: visitor + session number
    VISITOR_ID || '-' || SUM(is_session_start) OVER (
        PARTITION BY VISITOR_ID
        ORDER BY EVENT_TIME_UTC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS session_id
FROM flagged
