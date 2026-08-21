/*
  Transformation: Slowly Changing Dimension Type 2 (dbt snapshot)
  ---------------------------------------------------------------
  An SCD Type 2 keeps history: instead of overwriting a dimension row when an
  attribute changes, it closes the old version and opens a new one, so every past
  state remains queryable. dbt's snapshot does this for you — on each run it
  compares the source to the stored table and, when a tracked column changes for
  a key, stamps dbt_valid_to on the old row and inserts a new current row
  (dbt_valid_to IS NULL marks the live version).

  When to use it: to track change over time on a dimension whose source only ever
  shows the current state — a visitor's device/country as it evolves, a product's
  price history — enabling "what was true on date X" point-in-time joins. This is
  the historisation pattern none of the row-in/row-out models above can express.
  The query below reduces the event stream to one current state per visitor; the
  snapshot turns successive states into history.
*/
{% snapshot visitor_scd2 %}

{{ config(
    target_database=env_var('DBT_SILVER_DATABASE'),
    target_schema=env_var('DBT_SILVER_SCHEMA'),
    unique_key='visitor_id',
    strategy='check',
    check_cols=['device_type', 'geo_country']
) }}

WITH current_state AS (
    SELECT
        VISITOR_ID AS visitor_id,
        DEVICE_TYPE AS device_type,
        GEO_COUNTRY AS geo_country
    FROM {{ source('studios_piano', 'studios_piano_events') }}
    -- Latest observed attributes per visitor = their current dimension state
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY VISITOR_ID ORDER BY EVENT_TIME_UTC DESC
    ) = 1
)

SELECT * FROM current_state

{% endsnapshot %}
