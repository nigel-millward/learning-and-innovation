/*
  Transformation: Null Handling & Coalescing
  -------------------------------------------
  Null handling replaces missing values with a sensible default so downstream
  logic and aggregates behave predictably. COALESCE returns the first non-null
  of its arguments; NVL is the two-argument form; NULLIF turns a sentinel value
  (like '') back into a NULL. The row count never changes — only the gaps fill.

  When to use it: at the silver layer to give every column a defined value
  before it is grouped, joined, or charted — NULLs silently drop out of GROUP BY
  keys and break equality joins. Pick a default that is unambiguous and cannot
  be confused with a real value ('unknown', not '').
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    -- COALESCE: fall back through several columns to a literal default
    COALESCE(GEO_COUNTRY, GEO_CONTINENT, 'unknown') AS country_filled,
    -- NVL: simple two-argument default for a dimension
    NVL(DEVICE_TYPE, 'unknown') AS device_type_filled,
    -- NULLIF: treat empty string as a real NULL, then default it
    COALESCE(NULLIF(TRIM(BROWSER), ''), 'unknown') AS browser_filled
FROM {{ source('studios_piano', 'studios_piano_events') }}
