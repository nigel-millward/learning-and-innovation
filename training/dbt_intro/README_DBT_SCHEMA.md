# DBT Model Properties

## What are model properties
Resources in your project—models, snapshots, seeds, tests, and the rest—can have a number of declared properties. Resources can also define configurations, which are a special kind of property that bring extra abilities

A rule of thumb: properties declare things about your project resources; configs go the extra step of telling dbt how to build those resources in your warehouse. This is generally true, but not always, so it's always good to check!

For example, you can use resource properties to:
- Describe models, snapshots, seed files, and their columns
- Assert "truths" about a model, in the form of data tests, e.g. "this id column is unique"
- Define pointers to existing tables that contain raw data, in the form of sources, and assert the expected "freshness" of this raw data
- Define official downstream uses of your data models, in the form of exposures 

Whereas you can use configurations to:
- Change how a model will be materialized (table, view, incremental, etc)
- Declare where a seed will be created in the database (<database>.<schema>.<alias>)
- Declare whether a resource should persist its descriptions as comments in the database
- Apply tags and "meta" properties


## Properties file

Models properties can be declared in .yml files in your models/ directory (as defined by the model-paths config).

You can name these files whatever_you_want.yml, historically they would be called schema.yml. 
And nest them arbitrarily deeply in subfolders within the models/ directory.

By default, we have been adding schema files at the root model path:
- models/gold/
- models/silver/
- models/schema.yml

## Example schema file
```
models:
  - name: PIANO_EVENTS
    description: "Table in silver layer that captures entire visit history from PIANO"

  - name: DAILY_ACTIVE_USERS
    description: "Table in gold layer to capture daily Active users"
    columns:
      - name: DATE
        tests:
          - not_null
      - name: BBCS_LOGICAL_SITE
        tests:
          - not_null
          - dbt_utils.not_empty_string:
              trim_whitespace: true
          - accepted_values:
              values: ['bbc.com', 'bbc.com Test', 'Britbox', 'BBC Player']
      - name: COUNTRY
        tests:
          - not_null
          - dbt_utils.not_empty_string:
              trim_whitespace: true
      - name: REGION
        tests:
          - not_null
          - dbt_utils.not_empty_string:
              trim_whitespace: true
      - name: PLATFORM
        tests:
          - not_null
          - dbt_utils.not_empty_string:
              trim_whitespace: true
      - name: ACTIVE_USERS
        tests:
          - not_null
    tests:
      - dbt_utils.recency:
          field: DATE
          datepart: day
          interval: 1
          ignore_time_component: True
```


More details on dbt sources: 
- https://docs.getdbt.com/reference/configs-and-properties
- https://docs.getdbt.com/reference/model-properties

