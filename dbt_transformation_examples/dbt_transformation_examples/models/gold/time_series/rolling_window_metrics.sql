/*
  Transformation: Rolling Window Metrics (moving averages over time)
  ------------------------------------------------------------------
  A rolling-window metric aggregates over a sliding frame of time-ordered rows
  relative to each row — a moving average, rolling sum, or trailing count. It
  uses a window function whose frame (ROWS/RANGE BETWEEN ... PRECEDING AND
  CURRENT ROW) defines how many prior periods are included.

  When to use it: to smooth noisy daily series and expose trend — a 7-day moving
  average of events damps weekday seasonality so a real shift stands out. Build
  it on an already-resampled regular grid (see resampling) so each frame covers
  a consistent span of time.
*/
{{ config(materialized='table') }}

WITH daily_counts AS (
    -- Regular daily grid first so the frame spans consistent periods
    SELECT
        DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
        COUNT(*) AS event_count
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    GROUP BY DATE_TRUNC('DAY', EVENT_TIME_UTC)
)

SELECT
    event_day,
    event_count,
    -- 7-day trailing moving average over the time-ordered frame
    AVG(event_count) OVER (
        ORDER BY event_day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS event_count_7d_avg
FROM daily_counts
