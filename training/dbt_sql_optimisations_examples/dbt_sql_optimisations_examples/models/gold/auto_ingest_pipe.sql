/*
  Technique: Auto-Ingest / COPY INTO File-Size Optimisation
  ---------------------------------------------------------
  Snowflake loads data in parallel, one file per thread, and a warehouse has a
  fixed number of threads per node. Ingest is fastest when staged files are
  sized to match that parallelism: roughly 100-250 MB compressed each. Too few
  huge files leave threads idle; thousands of tiny files waste per-file
  overhead.

  Why it is useful: matching file size to the warehouse's parallel slots keeps
  every thread busy and minimises load time and credits, whether loading via a
  one-off COPY INTO or a continuous Snowpipe. This is an ingestion-layer
  concern, so the loading statements below are reference SQL (run against the
  bronze landing target, not part of this model's SELECT). The model itself
  simply projects the ideal target structure for the loaded events.

    -- Optimised reference: size staged files ~100-250 MB compressed before COPY/Snowpipe
    -- COPY INTO sdp_bronze.studios_piano.events_raw
    --   FROM @studios_piano_stage
    --   FILE_FORMAT = (TYPE = PARQUET)
    --   MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
    -- CREATE PIPE studios_piano_pipe AUTO_INGEST = TRUE AS
    --   COPY INTO sdp_bronze.studios_piano.events_raw FROM @studios_piano_stage;
*/
{{ config(materialized='table') }}

SELECT
    EVENT_ID,
    EVENT_TIME_UTC,
    VISITOR_ID,
    SITE_ID,
    EVENT_NAME
FROM {{ source('studios_piano', 'studios_piano_events') }}
