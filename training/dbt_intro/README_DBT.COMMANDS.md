# DBT Commands

## Parallel execution
dbt Cloud allows for concurrent execution of commands, enhancing efficiency without compromising data integrity. This enables you to run multiple commands at the same time. However, it's important to understand which commands can be run in parallel and which can't.

In contrast, dbt-core doesn't support safe parallel execution for multiple invocations in the same process, and requires users to manage concurrency manually to ensure data integrity and system stability.

dbt commands can be read or write commands:

| Command Type | Description                                                                                                                                                                                       | Example |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| Write        | 	These commands perform actions that change data or metadata in your data platform.Limited to one invocation at any given time, which prevents any potential conflicts, such as overwriting the same table in your data platform at the same time. | dbt build, dbt run |
| Read         | These commands involve operations that fetch or read data without making any changes to your data platform. Can have multiple invocations in parallel and aren't limited to one invocation at any given time. This means read commands can run in parallel with other read commands and a single write command.| dbt parse, dbt compile |


## Basic dbt commands
**dbt init**
This command creates a new dbt project. It sets up the necessary directory structure and provides some example models to get you started. Here’s how you use it:


``` dbt init my_new_project ```

**dbt debug**
This command checks your dbt project setup. It verifies that your profiles.yml file is set up correctly, that dbt can connect to your data warehouse, and that all dependencies are installed. Here’s how you use it:

``` dbt debug ```

**dbt deps**
This command is used to download and manage the dbt packages that your project depends on. It reads your packages.yml file and installs all the packages listed there. Here’s how you use it:

```dbt deps```

**dbt clean**
This command cleans up your dbt project by deleting the dbt_modules and target directories. It’s useful when you want to ensure that you’re working with the most recent versions of your dbt packages and models. Here’s how you use it:

```dbt clean```

## Data Loading and Transformation
**dbt seed**
This command loads CSV files into your data warehouse. It’s useful when you have small data files that you want to use in your transformations. Here’s how you use it:

```dbt seed```

**dbt run**
This command runs transformations in your dbt project. It uses the model SQL files in your project to transform your raw data into analysis-ready tables. Here’s how you use it:

```dbt run```

**dbt snapshot**
This command is used to track changes in your data over time. It’s useful when you have slowly changing dimensions and you want to keep a history of changes. Here’s how you use it:

```dbt snapshot```

## Testing in dbt
**dbt test**
This command runs tests in your dbt project. It’s used to ensure that your transformations are working as expected and that your data meets the defined quality standards. Here’s how you use it:

```dbt test```

**dbt compile**
This command compiles your dbt project to check for errors. It doesn’t run the transformations, but it does generate the SQL that would be run, which can be useful for debugging. Here’s how you use it:

```dbt compile```

### Documentation and Metadata
**dbt docs generate**
This command generates documentation for your dbt project. It reads your model, test, and schema files and creates a set of documentation that describes your project. Here’s how you use it:

```dbt docs generate```

**dbt docs serve**
This command serves your dbt project documentation locally, allowing you to view it in your web browser. Here’s how you use it:

```dbt docs serve```

More details on dbt commands:
- https://docs.getdbt.com/reference/dbt-commands






More details on dbt sources: 
- https://docs.getdbt.com/docs/core/connect-data-platform/profiles.yml
- https://docs.getdbt.com/docs/core/connect-data-platform/connection-profiles


