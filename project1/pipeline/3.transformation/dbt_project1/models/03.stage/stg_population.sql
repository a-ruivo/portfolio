
{{ config(materialized='table') }}

with source_data as (
select
*
from {{ source('dados_ibge', 'populacao') }}
)

select *
from source_data
