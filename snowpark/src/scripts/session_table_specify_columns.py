# script to specify columns and expressions
from snowflake.snowpark.functions import col
from snowpark.src.libs.session import SnowflakeSession

session = SnowflakeSession().create()

# To create a DataFrame to hold the results of a SQL query, call the sql method
gam_api_table = "GAM_TEST_TABLE"
gam_df = session.table([
    session.get_current_database(),
    session.get_current_schema(),
    gam_api_table]).select(col("DIMENSION_DATE"))

gam_df.show(10)
print(type(gam_df))
gam_df.explain()

session.close()

