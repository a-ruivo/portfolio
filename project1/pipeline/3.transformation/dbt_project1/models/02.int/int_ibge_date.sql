
{{ config(materialized='table') }}

with source_data as (
select
    1 as date_id
    ,2000 as year_num
union
select
    2 as date_id
    ,2010 as year_num
union
select
    3 as date_id
    ,2022 as year_num
)

select *
from source_data
