/*
  Transformation: Text Tokenisation (string -> word / n-gram array)
  -----------------------------------------------------------------
  Tokenisation splits a text value into its component tokens — words or
  n-grams — producing an array. SPLIT divides on a literal delimiter;
  STRTOK_TO_ARRAY splits on any of several delimiter characters, which handles
  real text with mixed separators. The array can then be flattened, counted, or
  fed to a text-feature pipeline.

  When to use it: as the first step of any word-level text analysis — term
  frequencies, keyword extraction, bag-of-words features. Lower-case first so
  the same word in different cases tokenises to one term, and pair this with
  FLATTEN (see the structural group) to count individual tokens.
*/
{{ config(materialized='table') }}

SELECT
    EVENT_ID,
    PAGE_TITLE,
    -- STRTOK_TO_ARRAY splits on any of the given delimiter characters
    STRTOK_TO_ARRAY(LOWER(PAGE_TITLE), ' ,.;:!?') AS title_tokens,
    -- Token count straight off the resulting array
    ARRAY_SIZE(STRTOK_TO_ARRAY(LOWER(PAGE_TITLE), ' ,.;:!?')) AS title_token_count
FROM {{ source('studios_piano', 'studios_piano_events') }}
WHERE PAGE_TITLE IS NOT NULL
