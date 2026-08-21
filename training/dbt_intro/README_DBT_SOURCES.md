# DBT Sources

## Using Sources
Sources make it possible to name and describe the data loaded into your warehouse by your Extract and Load tools. By declaring these tables as sources in dbt, you can then

- select from source tables in your models using the {{ source() }} function, helping define the lineage of your data
- test your assumptions about your source data
- calculate the freshness of your source data

## Declaring a source
Sources are defined in .yml files nested under a sources: key.

models/gold
models/silver
models/schema.yml

```
version: 2

sources:
  - name: jaffle_shop
    database: raw  
    schema: jaffle_shop  
    tables:
      - name: orders
      - name: customers

  - name: stripe
    tables:
      - name: payments 
```

## Select from a source
Once a source has been defined, it can be referenced from a model using the {{ source()}} function.

```
select
  ...

from {{ source('jaffle_shop', 'orders') }}

left join {{ source('jaffle_shop', 'customers') }} using (customer_id)
```

More details on dbt sources: 
- https://docs.getdbt.com/docs/build/sources
- 

