WITH employee_ranking AS (
  SELECT
    employee_id,
    last_name,
    first_name,
    salary,
    NTILE(4) OVER (ORDER BY salary) as ntile
  FROM employee
)
SELECT
  employee_id,
  last_name,
  first_name,
  salary
FROM employee_ranking
WHERE ntile = 4
ORDER BY salary