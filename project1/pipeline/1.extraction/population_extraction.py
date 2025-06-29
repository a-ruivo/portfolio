import requests
import duckdb
import pandas as pd
import os
from dotenv import load_dotenv

# Path to DuckDB file
DUCKDB_PATH = "/opt/airflow/shared_data/ibge_duckdb.db"

# Load .env variables
load_dotenv()

# Validate required environment variables
required_vars = ["DB_NAME", "DB_USER", "DB_PASSWORD"]
missing = [var for var in required_vars if os.getenv(var) is None]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

# IBGE API endpoint
URL = "https://servicodados.ibge.gov.br/api/v3/agregados/1209/periodos/2000|2010|2022/variaveis/606?localidades=N3[all]&classificacao=58[all]"

def fetch_json():
    print("[1/4] Fetching data from IBGE API...")
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Failed to access IBGE API: {response.status_code}")

def expand_age_groups(json_data):
    print("[2/4] Expanding series by locality and age group...")
    registros = []

    resultados = json_data[0].get("resultados", [])
    for resultado in resultados:
        classificacoes = resultado.get("classificacoes", [])
        if not classificacoes:
            continue

        categorias = classificacoes[0].get("categoria", {})
        for codigo, faixa_etaria in categorias.items():
            if faixa_etaria.lower() == "total":
                continue  # skip total

            for item in resultado.get("series", []):
                loc = item.get("localidade", {})
                serie = item.get("serie", {})

                registros.append({
                    "nome": json_data[0].get("variavel", "População"),
                    "grupo_idade": faixa_etaria,
                    "localidade": loc.get("nome"),
                    "serie_2000": serie.get("2000"),
                    "serie_2010": serie.get("2010"),
                    "serie_2022": serie.get("2022")
                })

    df = pd.DataFrame(registros)
    print(f"Loaded {len(df)} rows from classified series")
    return df

def create_duckdb_table():
    print("[3/4] Creating simplified table in DuckDB...")
    conn = duckdb.connect(DUCKDB_PATH)
    conn.execute("DROP TABLE IF EXISTS ibge_populacao_etaria")
    conn.execute("""
        CREATE TABLE ibge_populacao_etaria (
            nome VARCHAR,
            grupo_idade VARCHAR,
            localidade VARCHAR,
            serie_2000 VARCHAR,
            serie_2010 VARCHAR,
            serie_2022 VARCHAR
        )
    """)
    conn.close()

def insert_into_duckdb(df):
    print("[4/4] Inserting records into DuckDB...")
    conn = duckdb.connect(DUCKDB_PATH)
    conn.executemany(
        """
        INSERT INTO ibge_populacao_etaria 
        (nome, grupo_idade, localidade, serie_2000, serie_2010, serie_2022)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        df[['nome', 'grupo_idade', 'localidade', 'serie_2000', 'serie_2010', 'serie_2022']].itertuples(index=False, name=None)
    )
    conn.close()

def run_etl():
    json_data = fetch_json()
    df = expand_age_groups(json_data)
    df.to_csv("ibge_populacao_faixa_etaria.csv", index=False)
    create_duckdb_table()
    insert_into_duckdb(df)
    print("ETL completed successfully. Data saved to ibge_populacao_etaria table.")


if __name__ == "__main__":
    run_etl()