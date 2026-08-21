/*
  Transformation: Date Spine & Gap Filling (forward-fill / LOCF)
  -------------------------------------------------------------
  A date spine is a generated, gap-free sequence of periods. Left-joining real
  measurements onto it makes missing periods explicit rows rather than absent
  dates — the true form of upsampling that resampling alone cannot produce. Once
  the grid is complete, gaps can be filled two ways: with a zero/default for
  count-like measures, or by carrying the last observed value forward (LOCF) for
  state-like measures using LAST_VALUE(... IGNORE NULLS) over the ordered spine.

  When to use it: before any period-over-period chart or moving average, where a
  day with no events must read as 0 (or as "same state as yesterday") rather than
  silently disappearing and distorting the trend. The spine is built here with a
  recursive CTE to stay self-contained; dbt_utils.date_spine() packages exactly
  this pattern as a reusable macro.
*/
{{ config(materialized='table') }}

WITH RECURSIVE bounds AS (
    SELECT
        MIN(DATE_TRUNC('DAY', EVENT_TIME_UTC)) AS min_day,
        MAX(DATE_TRUNC('DAY', EVENT_TIME_UTC)) AS max_day
    FROM {{ source('studios_piano', 'studios_piano_events') }}
),

-- Recursive CTE walks one day at a time from min_day to max_day
spine AS (
    SELECT min_day AS date_day
    FROM bounds
    UNION ALL
    SELECT DATEADD('DAY', 1, s.date_day)
    FROM spine AS s
    INNER JOIN bounds AS b
        ON s.date_day < b.max_day
),

daily_events AS (
    SELECT
        DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
        COUNT(*) AS event_count
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    GROUP BY DATE_TRUNC('DAY', EVENT_TIME_UTC)
)

SELECT
    s.date_day AS event_day,
    -- Zero-fill: a count measure is 0 on days with no events
    COALESCE(d.event_count, 0) AS event_count,
    -- Forward-fill (LOCF): carry the last non-null observed count forward
    LAST_VALUE(d.event_count IGNORE NULLS) OVER (
        ORDER BY s.date_day
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS event_count_locf
FROM spine AS s
LEFT JOIN daily_events AS d
    ON s.date_day = d.event_day
ORDER BY s.date_day
