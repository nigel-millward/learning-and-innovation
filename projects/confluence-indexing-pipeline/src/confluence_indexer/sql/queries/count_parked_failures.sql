-- Pages that exhausted their retries and need a human.
SELECT count(*) AS n
FROM confluence_index.failed_pages
WHERE attempts >= %(max_attempts)s;
