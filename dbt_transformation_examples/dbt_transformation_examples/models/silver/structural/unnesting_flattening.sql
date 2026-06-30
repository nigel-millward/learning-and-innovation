/*
  Transformation: Unnesting / Flattening (array -> rows)
  ------------------------------------------------------
  Unnesting expands a semi-structured column (VARIANT array or object) into one
  row per element, lifting nested values up to the relational level. In
  Snowflake this is LATERAL FLATTEN, which streams each element of the array out
  alongside its parent row in a single pass over the table.

  When to use it: when a column holds a collection — tags, line items, an event
  payload array — and you need to query, join, or aggregate the individual
  elements. Flattening converts "one row with N values inside" into "N rows",
  the shape relational operators expect.
*/
{{ config(materialized='view') }}

SELECT
    e.EVENT_ID,
    e.EVENT_TIME_UTC,
    e.VISITOR_ID,
    -- FLATTEN emits one row per array element; tag.value is the element
    tag.value::STRING AS tag_value,
    tag.index AS tag_position
FROM {{ source('studios_piano', 'studios_piano_events') }} AS e,
    LATERAL FLATTEN(input => e.TAGS_ARRAY) AS tag
