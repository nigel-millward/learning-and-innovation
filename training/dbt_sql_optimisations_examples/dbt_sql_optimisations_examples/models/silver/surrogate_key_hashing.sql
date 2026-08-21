/*
  Technique: Surrogate Key Hashing with *_BINARY functions
  --------------------------------------------------------
  Build surrogate keys with MD5_BINARY (or SHA2_BINARY) so the key is stored as
  a 16-byte BINARY value rather than a 32-character hex STRING. The binary form
  is roughly half the size on disk and in memory.

  Why it is useful: surrogate keys are used as join keys, so they are read,
  hashed and compared constantly. A BINARY key halves the storage footprint and
  — more importantly — halves the memory each row's key occupies in join hash
  tables, which reduces spilling on large joins and speeds up the join itself.
  The win only shows when the key is actually used in a join, so this model
  builds the key in one CTE and joins on it in the next.
*/
{{ config(materialized='view') }}

WITH events AS (
    SELECT
        EVENT_ID,
        EVENT_TIME_UTC,
        VISITOR_ID,
        SITE_ID,
        EVENT_NAME,
        -- Optimised line: MD5_BINARY yields a 16-byte BINARY key (half the size of a 32-char hex string)
        MD5_BINARY(EVENT_ID || '|' || VISITOR_ID) AS event_visitor_sk
    FROM {{ source('studios_piano', 'studios_piano_events') }}
),

visitor_first_seen AS (
    SELECT
        MD5_BINARY(EVENT_ID || '|' || VISITOR_ID) AS event_visitor_sk,
        MIN(EVENT_TIME_UTC) AS first_seen_utc
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    GROUP BY MD5_BINARY(EVENT_ID || '|' || VISITOR_ID)
)

SELECT
    e.event_visitor_sk,
    e.EVENT_ID,
    e.VISITOR_ID,
    e.SITE_ID,
    e.EVENT_NAME,
    e.EVENT_TIME_UTC,
    v.first_seen_utc
FROM events AS e
-- The binary surrogate key is the join key: smaller key = smaller join hash table = less memory/spill
INNER JOIN visitor_first_seen AS v
    ON e.event_visitor_sk = v.event_visitor_sk
