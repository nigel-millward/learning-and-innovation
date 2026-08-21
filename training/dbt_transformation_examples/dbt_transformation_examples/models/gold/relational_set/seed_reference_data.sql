/*
  Transformation: Seed Reference Data (version-controlled lookups)
  ----------------------------------------------------------------
  A dbt seed is a small CSV checked into the repo and loaded as a table by
  `dbt seed`. It is the right home for stable, human-maintained reference data —
  code/label maps, flags, thresholds — that has no upstream source. Unlike the
  inline VALUES stand-ins used elsewhere in this project, a seed is referenced
  with ref() exactly like a model, so lineage and tests apply to it.

  When to use it: when an enrichment table is small, changes rarely, and is owned
  by the analytics team rather than a source system — here mapping SITE_ID to a
  friendly name, region, and an internal-traffic flag. Contrast with lookup,
  which derived its reference inline from the source.
*/
{{ config(materialized='table') }}

SELECT
    e.EVENT_ID,
    e.SITE_ID,
    -- Attributes supplied by the version-controlled seed, defaulted on no match
    COALESCE(r.site_name, 'unknown') AS site_name,
    COALESCE(r.region, 'unknown') AS region,
    COALESCE(r.is_internal, FALSE) AS is_internal
FROM {{ source('studios_piano', 'studios_piano_events') }} AS e
LEFT JOIN {{ ref('site_reference') }} AS r
    ON e.SITE_ID = r.site_id
