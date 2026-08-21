/*
  Transformation: Window Functions (per-row calculations over a partition)
  ------------------------------------------------------------------------
  A window function computes across a set of rows related to the current row
  (the "window") without collapsing them — unlike GROUP BY, every input row is
  preserved and gains a new column. The OVER clause defines the partition (which
  rows share a window), the order, and optionally a frame. This powers running
  totals, ranks, and lead/lag comparisons.

  When to use it: when you need both the detail row and a calculation over its
  neighbours — a row's rank within its group, a running cumulative total, or the
  gap to the previous event for the same visitor. It is the row-preserving
  cousin of aggregation.
*/
{{ config(materialized='table') }}

SELECT
    EVENT_ID,
    VISITOR_ID,
    EVENT_TIME_UTC,
    -- Rank events within each visitor by time
    ROW_NUMBER() OVER (
        PARTITION BY VISITOR_ID ORDER BY EVENT_TIME_UTC
    ) AS event_seq,
    -- Running count of events for the visitor up to this row
    COUNT(*) OVER (
        PARTITION BY VISITOR_ID
        ORDER BY EVENT_TIME_UTC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_event_count,
    -- LAG: seconds since this visitor's previous event
    DATEDIFF(
        'SECOND',
        LAG(EVENT_TIME_UTC) OVER (
            PARTITION BY VISITOR_ID ORDER BY EVENT_TIME_UTC
        ),
        EVENT_TIME_UTC
    ) AS secs_since_prev_event
FROM {{ source('studios_piano', 'studios_piano_events') }}
