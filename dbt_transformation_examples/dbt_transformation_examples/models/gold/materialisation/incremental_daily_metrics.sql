/*
  Transformation: Incremental Materialisation (process only new data)
  -------------------------------------------------------------------
  An incremental model builds the table once, then on subsequent runs transforms
  and merges *only the new or changed source rows* instead of rebuilding from
  scratch. The is_incremental() block adds a filter that, on incremental runs,
  reads the current max watermark from {{ this }} and selects only newer source
  rows; unique_key tells dbt to MERGE so re-processed rows update in place rather
  than duplicating.

  When to use it: on large, append-mostly fact tables where a full refresh is too
  slow or costly — the canonical dbt pattern for scaling gold aggregates. Choose
  a reliable watermark column and a unique_key; a late-arriving-data lookback
  window (subtract an interval from the max) trades a little rework for safety.
*/
{{ config(
    materialized='incremental',
    unique_key='event_day',
    incremental_strategy='merge'
) }}

SELECT
    DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
    COUNT(*) AS event_count,
    COUNT(DISTINCT VISITOR_ID) AS unique_visitors
FROM {{ source('studios_piano', 'studios_piano_events') }}

{% if is_incremental() %}
    -- Only reprocess recent days; a 1-day lookback absorbs late-arriving events
    WHERE DATE_TRUNC('DAY', EVENT_TIME_UTC) >= (
        SELECT DATEADD('DAY', -1, MAX(event_day)) FROM {{ this }}
    )
{% endif %}

GROUP BY DATE_TRUNC('DAY', EVENT_TIME_UTC)
