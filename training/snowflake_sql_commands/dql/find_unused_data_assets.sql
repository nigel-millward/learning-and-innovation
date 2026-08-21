with
access_history as (

SELECT
    ah.query_id,
    ah.query_start_time,
    ah.user_name,
    qh.role_name,
    ah.base_objects_accessed
FROM
    snowflake.account_usage.access_history ah
LEFT JOIN snowflake.account_usage.query_history qh ON ah.query_id = qh.query_id

WHERE qh.role_name NOT IN ('SDP_PLATFORM_ENGINEER', 'SDP_SIFFLET', 'SDP_INFRASTRUCTURE', 'SDP_FIVETRAN', 'SNOWFLAKE', 'ACCOUNTADMIN', 'SYSADMIN', 'SDP_ARCHITECT', 'SDP_DATA_GOVERNANCE')

ORDER BY
    ah.query_start_time ASC 
),

access_history_flattened as (
    select
        access_history.query_id,
        access_history.query_start_time,
        access_history.user_name,
        access_history.role_name,
        objects_accessed.value:objectId::integer as table_id,
        objects_accessed.value:objectName::text as object_name,
        objects_accessed.value:objectDomain::text as object_domain,
        objects_accessed.value:columns as columns_array

    from access_history, lateral flatten(access_history.base_objects_accessed) as objects_accessed
),

table_access_history as (
	select
      query_id,
      query_start_time,
      role_name,
      user_name,
      SPLIT_PART(object_name, '.', 1) AS snowflake_database,
      SPLIT_PART(object_name, '.', 2) AS snowflake_schema,
      SPLIT_PART(object_name, '.', 3) AS snowflake_table,
	from access_history_flattened ahf
    inner JOIN SNOWFLAKE.ACCOUNT_USAGE.TABLES t ON ahf.table_id = t.table_id
    where t.deleted is null
    and snowflake_database in ('SDP_BRONZE', 'SDP_SILVER','SDP_GOLD')
)
select
    snowflake_database,
    snowflake_schema,
    snowflake_table,
    max(query_start_time) as last_accessed_at,
    max_by(user_name, query_start_time) as last_accessed_by,
    max_by(query_id, query_start_time) as last_query_id
from table_access_history
group by 1,2,3
having NOT last_accessed_at > DATEADD('month', -6, CURRENT_TIMESTAMP()) -- older than or equal to 6 months ago.
order by 1,2,3;







