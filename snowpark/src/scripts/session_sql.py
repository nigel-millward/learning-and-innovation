from snowpark.src.libs.session import SnowflakeSession

session = SnowflakeSession().create()

# To create a DataFrame to hold the results of a SQL query, call the sql method
gam_test_df = session.sql('''
SELECT * FROM SDP_BRONZE.GAM_TEST.GAM_TEST_TABLE limit 10
''')

gam_test_df.show(10)
print(type(gam_test_df))
gam_test_df.explain()

session.close()
