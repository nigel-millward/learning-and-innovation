/*
  Technique: Materialization Choice
  ----------------------------------
  Pick the materialization that matches how a model is used rather than
  defaulting everything to a table:
    - view      : cheap to build, always fresh, but recomputes on every read.
                  Best for light transforms read infrequently.
    - ephemeral : no object in Snowflake at all; dbt inlines the SQL as a CTE
                  into downstream models. Best for small reusable building
                  blocks that should not pay for their own storage or scan.
    - table     : pays storage + build cost once, then reads are fast. Best for
                  heavy transforms read many times (see the gold models).

  Why it is useful: this lightweight projection is read occasionally and stays
  cheap as a view — materialising it as a table would add storage and a build
  step for no benefit. Switching the line below to `ephemeral` would instead
  fold it straight into its consumers with no standalone object.
*/
-- Optimised line: a view (not a table) avoids storage + a build step for this light, infrequently-read transform
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    EVENT_TIME_UTC,
    SITE_ID,
    EVENT_NAME
FROM {{ source('studios_piano', 'studios_piano_events') }}
