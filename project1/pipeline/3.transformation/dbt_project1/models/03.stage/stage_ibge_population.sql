
{{ config(materialized='table') }}

with source_data as (
    select
        cast(localidade as varchar) as localidade
        ,cast(grupo_idade as varchar) as grupo_idade
        ,cast(replace(serie_2000,'...','0') as int) as serie_2000
        ,cast(replace(serie_2010,'...','0') as int) as serie_2010
        ,cast(replace(serie_2022,'...','0') as int) as serie_2022
from {{ source('ibge', 'ibge_populacao_etaria') }}
)

select *
from source_data
