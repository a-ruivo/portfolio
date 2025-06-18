
{{ config(materialized='table') }}

with source_data as (
select
    *
from {{ ref('int_ibge_date') }}
)

select *
from source_data
