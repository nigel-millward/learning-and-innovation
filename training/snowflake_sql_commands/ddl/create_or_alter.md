# Create or Alter

CREATE OR ALTER commands are DDL commands that combine the functionality of the CREATE command and the ALTER command,
enabling you to define an object using the syntax supported by the CREATE <object> command with the limitations of 
the ALTER <object> command.  

Create or Alter:
- If the table doesn’t exist, it’s created according to the definition.

- If the table exists, it’s altered into the object defined in the statement

- If the table already matches the definition, it remains unchanged.


The following changes are supported when altering a table:

- Change table properties and parameters. For example, ENABLE_SCHEMA_EVOLUTION, DATA_RETENTION_TIME_IN_DAYS, or CLUSTER BY.

- Change column data type, default value, nullability, comment, or autoincrement.

- Add new columns to the end of the column list.

- Drop columns.

- Add, drop, or modify inline or out-of-line constraints.

- Add, drop, or modify clustering keys.

### Use cases for core-data team

1. Create or alter statement may solve our problem for **data catalogue** comments.
So that we'd only need to maintain a single script using 'create or alter table', instead of 2 separate scripts: create table script and a separate alter script 


References:  
- https://docs.snowflake.com/en/sql-reference/sql/create-table
- https://docs.snowflake.com/en/sql-reference/sql/create-or-alter