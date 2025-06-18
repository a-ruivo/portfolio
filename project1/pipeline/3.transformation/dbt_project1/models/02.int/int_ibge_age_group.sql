
{{ config(materialized='table') }}

with source_data as (
select
    distinct
        grupo_idade as age_group_name_str
from {{ ref('stage_ibge_population') }}
)
select 
    *
    ,row_number() over(order by age_group_name_str) as age_group_id
from source_data
