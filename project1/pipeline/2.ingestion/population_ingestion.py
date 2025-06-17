import requests
import duckdb
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

# Caminho para o banco DuckDB
DUCKDB_PATH = "project1/pipeline/extraction/populacao_duckdb.db"

# Carrega variáveis do .env
load_dotenv()

# Validação das variáveis obrigatórias
required_vars = ["DB_NAME", "DB_USER", "DB_PASSWORD"]
missing = [var for var in required_vars if os.getenv(var) is None]
if missing:
    raise EnvironmentError(f"Variáveis ausentes no .env: {', '.join(missing)}")

# Configuração do PostgreSQL
PG_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

def exportar_para_postgres():
    print("Exportando dados para PostgreSQL...")
    conn_duckdb = duckdb.connect(DUCKDB_PATH)
    dados = conn_duckdb.execute("SELECT localidade_nome, ano, valor FROM populacao").fetchall()

    conn_pg = psycopg2.connect(**PG_CONFIG)
    cursor_pg = conn_pg.cursor()
    cursor_pg.execute("""
        CREATE TABLE IF NOT EXISTS populacao (
            location_name_str TEXT,
            year_num INT,
            population_qty INT,
            PRIMARY KEY (location_name_str, year_num)
        )
    """)
    for row in dados:
        try:
            cursor_pg.execute("""
                INSERT INTO populacao (location_name_str, year_num, population_qty)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """, row)
        except Exception as e:
            print("Erro ao inserir registro:", row, e)

    conn_pg.commit()
    cursor_pg.close()
    conn_pg.close()
    conn_duckdb.close()

def ingestion():
    exportar_para_postgres()
    print("Tudo pronto! Os dados foram enviados com sucesso.")

if __name__ == "__main__":
    ingestion()