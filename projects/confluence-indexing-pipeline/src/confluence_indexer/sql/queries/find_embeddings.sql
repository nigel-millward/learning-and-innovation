-- Existing vectors for any of these chunk hashes, from any page, so unchanged
-- (or moved, or duplicated) text is never sent to the embedding model twice.
SELECT DISTINCT ON (content_hash) content_hash, embedding
FROM confluence_index.chunks
WHERE embedding_version = %(embedding_version)s
  AND content_hash = ANY(%(content_hashes)s);
