import pandas as pd

df = pd.read_excel('Book1.xlsx', engine='openpyxl')

# convert the date column
df['LAST_ACCESSED_AT'] = pd.to_datetime(df['LAST_ACCESSED_AT'], errors='coerce', utc=True)

# create monthly bucket column
df['MONTH_BUCKET'] = df['LAST_ACCESSED_AT'].dt.to_period('M')

# create the pivot table
pivot = df.pivot_table(
    index='MONTH_BUCKET',
    values='SNOWFLAKE_TABLE',
    aggfunc='count'
).rename(columns={'SNOWFLAKE_TABLE': 'TABLE_COUNT'})

# reset the index
pivot = pivot.reset_index()

# export the pivot table
pivot.to_excel('snowflake_tables_by_month.xlsx', index=False)