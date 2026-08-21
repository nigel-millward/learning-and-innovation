/*
  Technique: General Recommendations (minor habits, one model)
  ------------------------------------------------------------
  A grab-bag of small, always-on habits that each save a little but do not
  warrant a model of their own. Several are demonstrated in the SELECT below;
  the inline comment marks the line for each.

  1. No ORDER BY in non-final models. Sorting is expensive and pointless in a
     model that downstream queries will re-process — the order is not preserved
     once another step reads it. Only sort in the final presentation query that
     actually needs ordered output.

  2. GROUP BY ALL. Group by every non-aggregated select-list item without
     re-typing the column list. It is purely a readability/maintenance win
     (Snowflake plans it identically to an explicit GROUP BY), but it stops the
     common bug where a new grouping column is added to SELECT and forgotten in
     GROUP BY.

  3. Tight window frames. An ordered window function defaults to the frame
     RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW. If you only need a
     single neighbouring row, state a narrow ROWS frame so Snowflake buffers
     fewer rows per partition.

  4. LIMIT for exploration. When eyeballing data, add LIMIT so Snowflake can
     stop early and prune partitions instead of materialising the full result.
     Never rely on LIMIT for correctness in a model — only as a scan-reducing
     habit while exploring.

  5. Warm warehouse (local disk) cache. Distinct from the result cache: a
     running warehouse keeps recently-read micro-partitions on local SSD, so
     back-to-back models over the same source re-read from cache. Grouping
     related work onto the same warehouse before it auto-suspends keeps that
     cache warm — nothing to write in SQL, just a scheduling habit.
*/
{{ config(materialized='view') }}

SELECT
    SITE_ID,
    DEVICE_TYPE,
    DATE_TRUNC('DAY', EVENT_TIME_UTC) AS event_day,
    COUNT(*) AS event_count,
    -- Optimised line (rec. 3): a narrow ROWS frame buffers fewer rows than the default RANGE frame
    SUM(COUNT(*)) OVER (
        PARTITION BY SITE_ID
        ORDER BY DATE_TRUNC('DAY', EVENT_TIME_UTC)
        ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
    ) AS rolling_2day_event_count
FROM {{ source('studios_piano', 'studios_piano_events') }}
-- Optimised line (rec. 2): GROUP BY ALL avoids drift between the SELECT list and the grouping keys
GROUP BY ALL
-- Optimised line (rec. 1): no ORDER BY here — this is not the final presentation query, so sorting would be wasted
