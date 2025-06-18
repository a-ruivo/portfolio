
{{ config(materialized='table') }}

with source_data as (
select
    *
from {{ ref('int_ibge_age_group') }}
)

select *
from source_data
