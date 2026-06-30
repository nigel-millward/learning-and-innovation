/*
  Transformation: Cryptographic Hashing (masking & surrogate keys)
  ----------------------------------------------------------------
  Hashing maps a value to a fixed-length digest with a one-way function
  (MD5, SHA2). The same input always yields the same hash, but the original
  cannot be recovered. Two common uses: masking sensitive identifiers, and
  minting a deterministic surrogate key from one or more natural keys.

  When to use it: to pseudonymise PII (hash a user id so analysts can count
  distinct users without seeing the id), or to build a stable join key across a
  composite of columns. Hash a delimited concatenation so that distinct field
  boundaries cannot collide ('a' + 'bc' vs 'ab' + 'c').
*/
{{ config(materialized='view') }}

SELECT
    EVENT_ID,
    -- Masking: SHA2 pseudonymises a high-cardinality identifier
    SHA2(VISITOR_ID, 256) AS visitor_id_hashed,
    -- Surrogate key: MD5 over a delimited composite of natural keys
    MD5(EVENT_ID || '|' || EVENT_TIME_UTC::STRING) AS event_surrogate_key
FROM {{ source('studios_piano', 'studios_piano_events') }}
