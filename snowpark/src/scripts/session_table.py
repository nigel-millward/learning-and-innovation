# script to create a dataframe from a table
from snowpark.src.libs.session import SnowflakeSession

session = SnowflakeSession().create()

# print values from session object to test
print("\n\t Current Account Name: ",session.get_current_account())
print("\t Current Role Name: ",session.get_current_role())
print("\t Current Warehouse Name: ",session.get_current_warehouse())
print("\t Current Database Name: ",session.get_current_database())
print("\t Current Schema Name: ",session.get_current_schema())
print("\t Fully Qualified Schema Name: ",session.get_fully_qualified_current_schema(),"\n")
print("Session Object Type:", type(session))

# To create a DataFrame from data in a table, view, or stream, call the table method:
gam_api_table = "GAM_TEST_TABLE"
gam_df = session.table([
    session.get_current_database(),
    session.get_current_schema(),
    gam_api_table])

gam_df.show(20)
print(type(gam_df))

# closing the session
session.close()



