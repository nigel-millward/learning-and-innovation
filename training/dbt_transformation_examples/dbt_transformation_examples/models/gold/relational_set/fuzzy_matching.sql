/*
  Transformation: Fuzzy / Approximate Matching
  --------------------------------------------
  Fuzzy matching links values that are not byte-equal but are close enough to be
  the same thing, using a string-similarity measure. EDITDISTANCE counts the
  single-character edits between two strings (lower = closer); JAROWINKLER_SIMILARITY
  scores 0–100 and rewards a shared prefix. A candidate is matched by joining
  against a canonical list and keeping the best-scoring pair above a threshold.

  When to use it: to reconcile dirty free-text against a controlled vocabulary —
  mistyped or variant device/browser names, country spellings, supplier names —
  where an exact join or simple value-mapping table would miss the near-misses.
  Always keep a threshold and review: fuzzy joins can fan out or mismatch.
*/
{{ config(materialized='table') }}

WITH canonical (canonical_browser) AS (
    SELECT * FROM VALUES
        ('chrome'), ('safari'), ('firefox'), ('edge'), ('samsung internet')
    AS t (canonical_browser)
),

observed AS (
    SELECT DISTINCT LOWER(TRIM(BROWSER)) AS browser_raw
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    WHERE BROWSER IS NOT NULL
),

scored AS (
    SELECT
        o.browser_raw,
        c.canonical_browser,
        EDITDISTANCE(o.browser_raw, c.canonical_browser) AS edit_distance,
        JAROWINKLER_SIMILARITY(o.browser_raw, c.canonical_browser) AS jw_similarity
    FROM observed AS o
    CROSS JOIN canonical AS c
)

-- Keep the single best canonical match per raw value above a similarity floor
SELECT
    browser_raw,
    canonical_browser AS matched_browser,
    edit_distance,
    jw_similarity
FROM scored
WHERE jw_similarity >= 80
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY browser_raw ORDER BY jw_similarity DESC, edit_distance ASC
) = 1
