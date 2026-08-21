/*
  Transformation: Vertical Set Operations (stack rows)
  ----------------------------------------------------
  Set operations combine two result sets that share a column layout by stacking
  them vertically. UNION ALL concatenates and keeps duplicates; UNION also
  de-duplicates; INTERSECT keeps rows present in both; EXCEPT keeps rows in the
  first but not the second. Unlike a join they add rows, not columns.

  When to use it: to append compatible datasets (this month + last month), or to
  compare two populations by membership — EXCEPT to find visitors active last
  period but not this one (churn), INTERSECT for those active in both. Prefer
  UNION ALL unless you specifically need duplicate removal, which costs a sort.
*/
{{ config(materialized='table') }}

WITH recent_visitors AS (
    SELECT DISTINCT VISITOR_ID
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    WHERE EVENT_TIME_UTC >= DATEADD('DAY', -7, CURRENT_DATE())
),

prior_visitors AS (
    SELECT DISTINCT VISITOR_ID
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    WHERE EVENT_TIME_UTC >= DATEADD('DAY', -14, CURRENT_DATE())
        AND EVENT_TIME_UTC < DATEADD('DAY', -7, CURRENT_DATE())
)

-- EXCEPT keeps prior-week visitors who did not return this week (churned)
SELECT VISITOR_ID
FROM prior_visitors
EXCEPT
SELECT VISITOR_ID
FROM recent_visitors
