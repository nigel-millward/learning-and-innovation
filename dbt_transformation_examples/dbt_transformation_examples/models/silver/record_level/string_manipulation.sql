/*
  Transformation: String Manipulation
  ------------------------------------
  String manipulation reshapes text values: trimming whitespace, normalising
  case, padding, extracting substrings, and pattern-based replacement with
  regular expressions. Each function returns a cleaned-up string for the same
  row; the row count is unchanged.

  When to use it: to standardise free-text and identifier columns before they
  are grouped or joined — collapsing "  Mobile " and "mobile" to one value,
  stripping prefixes, or extracting the meaningful part of a compound code.
  Cleaning strings here prevents the same logical value splitting into many
  groups downstream.
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    -- Trim + lowercase to canonicalise a dimension for grouping
    LOWER(TRIM(BROWSER)) AS browser_clean,
    -- Substring / left to take a fixed-length code
    LEFT(GEO_COUNTRY, 2) AS country_prefix,
    -- Regex replace to strip everything but digits from a noisy field
    REGEXP_REPLACE(OS_VERSION, '[^0-9]', '') AS os_version_digits,
    -- LPAD to produce a fixed-width key
    LPAD(SITE_ID::STRING, 6, '0') AS site_id_padded
FROM {{ source('studios_piano', 'studios_piano_events') }}
