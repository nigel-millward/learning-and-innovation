SELECT
  employee_id,
  last_name,
  first_name,
  dept_id,
  manager_id,
  salary
FROM employee
GROUP BY
  employee_id,
  last_name,
  first_name,
  dept_id,
  manager_id,
  salary
HAVING COUNT(*) > 1