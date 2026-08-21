/*
  Transformation: JSON / Semi-Structured Parsing (path extraction)
  ----------------------------------------------------------------
  Parsing lifts scalar values out of a semi-structured payload into typed,
  relational columns. PARSE_JSON turns a JSON string into a VARIANT; from there
  colon path notation (payload:key) and bracket indexing (payload:arr[0])
  navigate into it, GET_PATH does the same dynamically, and the :: cast (or
  TRY-cast) coerces the extracted VARIANT to a concrete type. This is the
  scalar-extraction counterpart to FLATTEN, which expands arrays into rows.

  When to use it: as the first step over a raw JSON/VARIANT column landed in
  bronze (event payloads, API responses), pulling the handful of fields the
  silver model needs into clean typed columns. The payload here is constructed
  inline to stand in for such a raw column.
*/
{{ config(materialized='view') }}

WITH raw AS (
    SELECT
        EVENT_ID,
        -- Stand-in for a raw JSON payload column landed in bronze
        PARSE_JSON(
            OBJECT_CONSTRUCT(
                'device', DEVICE_TYPE,
                'geo', OBJECT_CONSTRUCT('country', GEO_COUNTRY),
                'tags', TAGS_ARRAY
            )::STRING
        ) AS payload
    FROM {{ source('studios_piano', 'studios_piano_events') }}
)

SELECT
    EVENT_ID,
    -- Colon path notation + typed cast
    payload:device::STRING AS device_type,
    -- Nested object navigation
    payload:geo:country::STRING AS geo_country,
    -- Dynamic path access with GET_PATH
    GET_PATH(payload, 'geo.country')::STRING AS geo_country_via_get_path,
    -- Array element by index
    payload:tags[0]::STRING AS first_tag
FROM raw
