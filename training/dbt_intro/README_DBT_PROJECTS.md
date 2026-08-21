# DBT Projects
A dbt project informs dbt about the context of your project and how to transform your data (build your data sets). By design, dbt enforces the top-level structure of a dbt project such as the dbt_project.yml file, the models directory, the snapshots directory, and so on. Within the directories of the top-level, you can organize your project in any way that meets the needs of your organization and data pipeline.

At a minimum, all a project needs is the dbt_project.yml project configuration file. dbt supports a number of different resources, so a project may also include:

| Resource    | Description                                                                                                                                                                                       | 
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Model       | Each model lives in a single file and contains logic that either transforms raw data into a dataset that is ready for analytics or, more often, is an intermediate step in such a transformation. |
| macros      | Blocks of code that you can reuse multiple times.                                                                                                                                                                                                  |
| seeds       | CSV files with static data that you can load into your data platform with dbt.                                                                                                                                                                                                  | 
| snapshots   | A way to capture the state of your mutable tables so you can refer to it later. |
| sources     | A way to name and describe the data loaded into your warehouse by your Extract and Load tools.                                                                                                                                                                                               |
| data tests  | SQL queries that you can write to test the models and resources in your project.                                                                                                                                                                                                 | 


## Project configuration
Every dbt project includes a project configuration file called dbt_project.yml. It defines the directory of the dbt project and other project configurations.

| Yaml key   | value description                                                                                                                                                                                 | 
|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| name|	Your project’s name in snake case|
|version|	Version of your project|
|require-dbt-version|	Restrict your project to only work with a range of dbt Core versions|
|profile|	The profile dbt uses to connect to your data platform|
|model-paths|	Directories to where your model and source files live|
|seed-paths|	Directories to where your seed files live|
|test-paths|	Directories to where your test files live|
|analysis-paths|	Directories to where your analyses live|
|macro-paths|	Directories to where your macros live|
|snapshot-paths|	Directories to where your snapshots live|
|docs-paths|	Directories to where your docs blocks live|
|vars|	Project variables you want to use for data compilation|

# Best Practice
Below is a complete file tree of a project
```
Jaffle_shop
├── README.md
├── analyses
├── seeds
│   └── employees.csv
├── dbt_project.yml
├── macros
│   └── cents_to_dollars.sql
├── models
│   ├── intermediate
│   │   └── finance
│   │       ├── _int_finance__models.yml
│   │       └── int_payments_pivoted_to_orders.sql
│   ├── marts
│   │   ├── finance
│   │   │   ├── _finance__models.yml
│   │   │   ├── orders.sql
│   │   │   └── payments.sql
│   │   └── marketing
│   │       ├── _marketing__models.yml
│   │       └── customers.sql
│   ├── staging
│   │   ├── jaffle_shop
│   │   │   ├── _jaffle_shop__docs.md
│   │   │   ├── _jaffle_shop__models.yml
│   │   │   ├── _jaffle_shop__sources.yml
│   │   │   ├── base
│   │   │   │   ├── base_jaffle_shop__customers.sql
│   │   │   │   └── base_jaffle_shop__deleted_customers.sql
│   │   │   ├── stg_jaffle_shop__customers.sql
│   │   │   └── stg_jaffle_shop__orders.sql
│   │   └── stripe
│   │       ├── _stripe__models.yml
│   │       ├── _stripe__sources.yml
│   │       └── stg_stripe__payments.sql
│   └── utilities
│       └── all_dates.sql
├── packages.yml
├── snapshots
└── tests
    └── assert_positive_value_for_total_amount.sql
```

More details on dbt projects: 
- https://docs.getdbt.com/docs/build/projects
- https://docs.getdbt.com/reference/dbt_project.yml

