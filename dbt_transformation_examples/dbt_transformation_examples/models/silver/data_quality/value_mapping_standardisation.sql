/*
  Transformation: Value Mapping & Standardisation
  -----------------------------------------------
  Value mapping collapses many erratic representations of the same concept onto
  one canonical value. Source systems spell the same thing many ways
  ('iOS', 'ios', 'Apple iOS'); a mapping (a CASE, a DECODE, or a join to a
  crosswalk table) normalises them so each real-world value is one string.

  When to use it: before grouping or joining on a dirty categorical column.
  Without standardisation the same logical category splits across several
  groups and counts are wrong. Map to a controlled vocabulary at silver so every
  downstream model shares one set of category values.
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    OS AS os_raw,
    -- Map erratic source spellings onto a canonical operating-system family
    CASE
        WHEN LOWER(TRIM(OS)) IN ('ios', 'apple ios', 'iphone os') THEN 'iOS'
        WHEN LOWER(TRIM(OS)) IN ('android', 'google android') THEN 'Android'
        WHEN LOWER(TRIM(OS)) LIKE 'windows%' THEN 'Windows'
        WHEN LOWER(TRIM(OS)) IN ('mac os x', 'macos', 'osx') THEN 'macOS'
        WHEN LOWER(TRIM(OS)) LIKE 'linux%' THEN 'Linux'
        ELSE 'Other'
    END AS os_standardised
FROM {{ source('studios_piano', 'studios_piano_events') }}
