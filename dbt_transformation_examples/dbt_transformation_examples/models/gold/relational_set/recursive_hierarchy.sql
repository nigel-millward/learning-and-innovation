/*
  Transformation: Recursive Hierarchy Traversal (recursive CTE)
  -------------------------------------------------------------
  A recursive CTE walks a self-referencing parent/child table to flatten an
  arbitrary-depth hierarchy. The anchor member selects the roots; the recursive
  member repeatedly joins the previous level back to the table to find each
  level's children, accumulating depth and a root-to-node path until no more
  children are found.

  When to use it: to resolve tree structures of unknown depth into a queryable
  table — an organisation chart, a category taxonomy, a comment thread, a
  bill-of-materials. The hierarchy here is an inline stand-in so the example is
  self-contained; in practice the anchor and recursion would read a ref() to a
  dimension carrying a parent_id.
*/
{{ config(materialized='table') }}

WITH RECURSIVE categories (category_id, category_name, parent_id) AS (
    -- Inline stand-in for a self-referencing dimension table
    SELECT * FROM VALUES
        (1, 'all_content', NULL),
        (2, 'drama', 1),
        (3, 'comedy', 1),
        (4, 'period_drama', 2),
        (5, 'crime_drama', 2),
        (6, 'sitcom', 3)
    AS t (category_id, category_name, parent_id)
),

tree AS (
    -- Anchor: the roots (no parent)
    SELECT
        category_id,
        category_name,
        parent_id,
        1 AS depth,
        category_name AS path
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive member: attach each node to its parent in the level above
    SELECT
        c.category_id,
        c.category_name,
        c.parent_id,
        t.depth + 1 AS depth,
        t.path || ' > ' || c.category_name AS path
    FROM categories AS c
    INNER JOIN tree AS t
        ON c.parent_id = t.category_id
)

SELECT
    category_id,
    category_name,
    parent_id,
    depth,
    path
FROM tree
ORDER BY path
