/*
  Transformation: Lookup (enrich with reference / dimension data)
  ---------------------------------------------------------------
  A lookup is a join whose purpose is enrichment: each fact row is decorated with
  descriptive attributes fetched from a reference table on a key. It is a LEFT
  JOIN by intent — every fact row is preserved, and the reference simply supplies
  extra columns (often with a COALESCE default for unmatched keys).

  When to use it: to attach human-readable or grouping attributes to events — a
  country's region/continent, a product's category, a code's label. The
  reference here is built inline from the source; in practice it would be a
  ref() to a maintained dimension model.
*/
{{ config(materialized='table') }}

WITH country_region AS (
    -- Stand-in reference table: latest region seen per country
    SELECT
        GEO_COUNTRY,
        MAX(GEO_REGION) AS geo_region,
        MAX(GEO_CONTINENT) AS geo_continent
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    WHERE GEO_COUNTRY IS NOT NULL
    GROUP BY GEO_COUNTRY
)

SELECT
    e.EVENT_ID,
    e.VISITOR_ID,
    e.GEO_COUNTRY,
    -- Enriched attributes from the lookup, with a default for unmatched keys
    COALESCE(r.geo_region, 'unknown') AS geo_region,
    COALESCE(r.geo_continent, 'unknown') AS geo_continent
FROM {{ source('studios_piano', 'studios_piano_events') }} AS e
LEFT JOIN country_region AS r
    ON e.GEO_COUNTRY = r.GEO_COUNTRY
