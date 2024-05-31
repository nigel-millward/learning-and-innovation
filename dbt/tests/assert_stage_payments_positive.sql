with payments as (
    select * from {{ref('stage_orders')}}
)

select 
    order_id
    sum(amout) as total_amount

from payments

group by 1
having total_amount < 0
