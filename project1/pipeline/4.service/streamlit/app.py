import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

# Validating required env variables
required_vars = ["DB_NAME", "DB_USER", "DB_PASSWORD"]
missing = [var for var in required_vars if os.getenv(var) is None]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

# PostgreSQL config
PG_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}
# Conexão com o banco de dados
@st.cache_resource
def connect_db():
    return psycopg2.connect(**PG_CONFIG)

# Carregando os dados
@st.cache_data
def load_data():
    conn = connect_db()
    query = '''
    SELECT year_num, state_name_str, age_group_name_str, population_qty 
        FROM gold.mart_ibge_fact_population p
        left join gold.mart_ibge_dim_state s on s.state_id = p.state_id
        left join gold.mart_ibge_dim_age_group a on a.age_group_id = p.age_group_id
        left join gold.mart_ibge_dim_date d on d.date_id = p.date_id
    '''
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# App Streamlit
st.title("Brazil Population Anaylisis - IBGE Data")

df = load_data()

# 2. population_qty por state_name_str
st.subheader("Population by state")
fig2 = px.bar(df.groupby("state_name_str", as_index=False).sum(), x="state_name_str", y="population_qty")
st.plotly_chart(fig2)

# 1. population_qty por year_num
st.subheader("Population by year")
fig1 = px.bar(df.groupby("year_num", as_index=False).sum(), x="year_num", y="population_qty")
st.plotly_chart(fig1)

# 3. population_qty por age_group_str
st.subheader("Population by age group")
fig3 = px.bar(df.groupby("age_group_name_str", as_index=False).sum(), x="age_group_name_str", y="population_qty")
st.plotly_chart(fig3)

# 4. População Total
st.subheader("Agerage Population")
avg_pop = df["population_qty"].mean()
st.metric(label="Total", value=f"{avg_pop:,}")
