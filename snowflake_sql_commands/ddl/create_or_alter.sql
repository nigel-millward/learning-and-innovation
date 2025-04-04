CREATE TABLE OR ALTER SDP_BRONZE.CONTENT_METADATA_SEO.BBC_CONTENT_METADATA (
    -- Source columns
    ID VARCHAR NOT NULL COMMENT 'Unique identifier for content (e.g., urn:bbc:optimo:asset:c0rqpgp0999o)',
    PATH VARCHAR COMMENT 'URL path of the content (e.g., /news/articles/c0rqpgp0999o)',
    URL VARCHAR COMMENT 'HTTP link to the content',
    TITLE VARCHAR COMMENT 'Title of the content/article',
    Summary VARCHAR COMMENT 'Brief summary or description of the content',
    TYPE VARCHAR COMMENT 'Content type (e.g., article, video, live)',
    SUBTYPE VARCHAR COMMENT 'Content subtype (e.g., news, sport, reels)',
    FIRST_PUBLISHED_AT TIMESTAMP_NTZ COMMENT 'Timestamp when content was first published',
    LAST_PUBLISHED_AT TIMESTAMP_NTZ COMMENT 'Timestamp of most recent content update',

    -- Metadata columns
    _SOURCE_NAME VARCHAR NOT NULL COMMENT 'Name of source file containing this record',
    _SOURCE_DATE DATE NOT NULL COMMENT 'Date extracted from source file name',
    _INSERTED_UTC TIMESTAMP_NTZ DEFAULT SYSDATE() COMMENT 'Timestamp when record was loaded into Snowflake',

    -- Composite primary key to handle multiple versions of same article
    CONSTRAINT pkey1 PRIMARY KEY (ID, LAST_PUBLISHED_AT)
)
CLUSTER BY (LAST_PUBLISHED_AT)
COMMENT = 'Bronze layer table containing BBC content metadata for SEO analysis';