
{{ config(materialized='table') }}

with source_data as (
    select
    distinct
        localidade as state_name_str
    from {{ ref('stage_ibge_population') }}
)
select 
    *
    ,row_number() over(order by state_name_str) as state_id
from source_data
