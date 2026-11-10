-- A new Confluence version whose indexed content is unchanged.
UPDATE confluence_index.pages
SET version = %(version)s,
    last_modified = %(last_modified)s,
    last_modified_by = %(last_modified_by)s,
    raw_uri = %(raw_uri)s
WHERE page_id = %(page_id)s;
