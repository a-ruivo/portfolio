import requests
import duckdb
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DUCKDB_PATH = os.getenv("extraction_path")+"ibge_duckdb.db"

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
    dados = conn_duckdb.execute("SELECT series, nome, categoria_0, categoria_1140, categoria_1141, categoria_1142, categoria_1143, categoria_2792, categoria_92982, categoria_1144, categoria_1145, categoria_3299, categoria_3300, categoria_3301, categoria_3520, categoria_3244, categoria_3245, classificacoes, localidade_id, localidade_nivel_id, localidade_nivel_nome, localidade_nome, serie_2000, serie_2010, serie_2022 FROM ibge_populacao").fetchall()

    conn_pg = psycopg2.connect(**PG_CONFIG)
    cursor_pg = conn_pg.cursor()
    cursor_pg.execute("""
        CREATE TABLE ibge_populacao (
    series VARCHAR,
    nome VARCHAR,
    categoria_0 VARCHAR,
    categoria_1140 VARCHAR,
    categoria_1141 VARCHAR,
    categoria_1142 VARCHAR,
    categoria_1143 VARCHAR,
    categoria_2792 VARCHAR,
    categoria_92982 VARCHAR,
    categoria_1144 VARCHAR,
    categoria_1145 VARCHAR,
    categoria_3299 VARCHAR,
    categoria_3300 VARCHAR,
    categoria_3301 VARCHAR,
    categoria_3520 VARCHAR,
    categoria_3244 VARCHAR,
    categoria_3245 VARCHAR,
    classificacoes VARCHAR,
    localidade_id VARCHAR,
    localidade_nivel_id VARCHAR,
    localidade_nivel_nome VARCHAR,
    localidade_nome VARCHAR,
    serie_2000 VARCHAR,
    serie_2010 VARCHAR,
    serie_2022 VARCHAR
    );
    """)
    for row in dados:
        try:
            cursor_pg.execute("""
                INSERT INTO ibge_populacao (series, nome, categoria_0, categoria_1140, categoria_1141, categoria_1142, categoria_1143, categoria_2792, categoria_92982, categoria_1144, categoria_1145, categoria_3299, categoria_3300, categoria_3301, categoria_3520, categoria_3244, categoria_3245, classificacoes, localidade_id, localidade_nivel_id, localidade_nivel_nome, localidade_nome, serie_2000, serie_2010, serie_2022)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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