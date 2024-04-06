# Snowpark api 

### What is snowpark?
The Snowpark library provides an  API for querying and processing data in a data pipeline within snowflake. 
Using the Snowpark library, you can build applications that process data in Snowflake without moving data to the system where your application code runs

For example, you can also automate data transformation and processing by writing stored procedures and scheduling those procedures as tasks in Snowflake.

Snowpark api documentation can be found here:
https://docs.snowflake.com/developer-guide/snowpark/python/index

### Pandas
Snowpark heavily uses pandas dataframes for processing data

### Learning and innovation 
As part of learning and innovation day, I explored some simple scripts for snowpark api:
- session library - connect to snowflake
- table script - return values into a df for a table
- sql script - return values into a dataframe from an sql script

I also explored data engineering with snowpark, code samples can be found in the steps package:
- https://github.com/nigel-millward/sfguide-data-engineering-with-snowpark-python

### Next steps
- stored procedures
- user defined functions
- Machine learning
- Testing snow park
