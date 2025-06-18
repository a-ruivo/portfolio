
{{ config(materialized='table') }}

with source_data as (
select
    *
from {{ ref('int_ibge_population') }}
)

select *
from source_data
