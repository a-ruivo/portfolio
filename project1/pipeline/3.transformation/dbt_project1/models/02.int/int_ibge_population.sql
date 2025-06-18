
{{ config(materialized='table') }}

with pop_2000 as (
    select
    distinct
        localidade
        ,grupo_idade
        ,serie_2000 as population_qty
        ,1 as date_id
    from {{ ref('stage_ibge_population') }}
),
pop_2010 as (
    select
    distinct
        localidade
        ,grupo_idade
        ,serie_2010 as population_qty
        ,2 as date_id
    from {{ ref('stage_ibge_population') }}
),
pop_2022 as (
    select
    distinct
        localidade
        ,grupo_idade
        ,serie_2022 as population_qty
        ,3 as date_id
    from {{ ref('stage_ibge_population') }}
),
pop_union as (
    select *
    from pop_2010
    union
    select *
    from pop_2010
    union
    select *
    from pop_2022)
select
    row_number() over(order by a.age_group_id,s.state_id,date_id) as population_fact_id
    ,a.age_group_id
    ,s.state_id
    ,date_id
    ,population_qty
from pop_union p
left join {{ ref('mart_ibge_dim_age_group') }} a on a.age_group_name_str = p.grupo_idade
left join {{ ref('mart_ibge_dim_state') }} s on s.state_name_str = p.localidade

