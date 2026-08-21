# DBT Profile

## About Profiles.yml
If you're using dbt Core, you'll need a profiles.yml file that contains the connection details for your data platform. When you run dbt Core from the command line, it reads your dbt_project.yml file to find the profile name, and then looks for a profile with the same name in your profiles.yml file. This profile contains all the information dbt needs to connect to your data platform.

If you're using dbt Cloud, you can connect to your data platform directly in the dbt Cloud interface and don't need a profiles.yml file.

## Example profiles.yml
```
piano_ps_daily:
  outputs:
    piano_ps_daily:
      account: "{{ env_var('DBT_SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('DBT_SNOWFLAKE_USERNAME') }}"
      password: "{{ env_var('DBT_SNOWFLAKE_PASSWORD') }}"
      role: "{{ env_var('DBT_ETL_ROLE') }}"
      warehouse: "{{ env_var('DBT_ETL_WAREHOUSE') }}"
      database: "{{ env_var('DBT_SNOWFLAKE_DATABASE') }}"
      schema: "{{ env_var('DBT_SNOWFLAKE_SCHEMA') }}"
      threads: 5
      type: snowflake
  target: piano_ps_daily
```

More details on dbt sources: 
- https://docs.getdbt.com/docs/core/connect-data-platform/profiles.yml
- https://docs.getdbt.com/docs/core/connect-data-platform/connection-profiles


