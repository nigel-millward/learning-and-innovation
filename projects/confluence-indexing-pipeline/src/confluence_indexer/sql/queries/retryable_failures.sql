SELECT page_id
FROM confluence_index.failed_pages
WHERE attempts < %(max_attempts)s
ORDER BY page_id;
