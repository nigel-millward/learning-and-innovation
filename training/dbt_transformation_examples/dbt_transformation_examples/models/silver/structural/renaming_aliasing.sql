/*
  Transformation: Renaming & Aliasing
  ------------------------------------
  Renaming gives a column a new, standardised name with AS; aliasing does the
  same to a table or subquery. The values are untouched — only the label
  changes. This is how raw source names are mapped onto a consistent, readable
  vocabulary for downstream consumers.

  When to use it: whenever source column names are cryptic, inconsistent across
  feeds, or collide on a join. Standardising names at the silver layer (e.g.
  EVENT_TIME_UTC -> event_timestamp) means gold models and BI tools speak one
  vocabulary regardless of how each upstream system happened to name things.
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    EVENT_TIME_UTC AS event_timestamp,
    VISITOR_ID AS visitor_key,
    VISIT_ID AS visit_key,
    SITE_ID AS site_key,
    EVENT_NAME AS event_type,
    DEVICE_TYPE AS device_category,
    GEO_COUNTRY AS country
FROM {{ source('studios_piano', 'studios_piano_events') }}
