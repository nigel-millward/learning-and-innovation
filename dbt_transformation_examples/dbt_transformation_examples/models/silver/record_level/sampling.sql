/*
  Transformation: Sampling (select a representative subset)
  ---------------------------------------------------------
  Sampling returns a subset of rows so downstream work runs on less data.
  Snowflake's SAMPLE clause offers two modes: BERNOULLI/ROW samples each row
  independently with a given probability (good for a uniform statistical
  sample), while SYSTEM/BLOCK samples whole micro-partitions (much cheaper on
  huge tables, but coarser). A SEED makes the draw repeatable.

  When to use it: to develop and test transformations against a fraction of a
  large table for speed, to build a stable QA subset, or to draw a uniform
  sample for exploratory statistics. Use ROW sampling when statistical
  representativeness matters; BLOCK sampling when raw scan cost dominates.
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    VISITOR_ID,
    EVENT_TIME_UTC,
    SITE_ID
FROM {{ source('studios_piano', 'studios_piano_events') }}
-- Row-wise 10% sample, repeatable via the SEED
SAMPLE ROW (10) SEED (42)
