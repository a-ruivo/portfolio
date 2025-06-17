import requests
import duckdb
import psycopg2
import os
from dotenv import load_dotenv

DUCKDB_PATH = "project1/pipeline/extraction/cnae_duckdb.db"

load_dotenv()

required_vars = ["DB_NAME", "DB_USER", "DB_PASSWORD"]
missing = [var for var in required_vars if os.getenv(var) is None]
if missing:
    raise EnvironmentError(f"Variáveis ausentes no .env: {', '.join(missing)}")

PG_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

def exportar_para_postgres():
    print("Exportando dados para PostgreSQL")
    conn_duckdb = duckdb.connect(DUCKDB_PATH)
    dados = conn_duckdb.execute("SELECT id, descricao, observacoes FROM cnae").fetchall()

    conn_pg = psycopg2.connect(**PG_CONFIG)
    cursor_pg = conn_pg.cursor()
    cursor_pg.execute("""
        CREATE TABLE IF NOT EXISTS cnae_classe (
            id INT PRIMARY KEY,
            descricao TEXT,
            observacoes TEXT
        )
    """)

    for row in dados:
        try:
            cursor_pg.execute("""
                INSERT INTO cnae_classe (id, descricao, observacoes)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, row)
        except Exception as e:
            print("Erro ao inserir linha:", row, e)

    conn_pg.commit()
    cursor_pg.close()
    conn_pg.close()
    conn_duckdb.close()

def ingestion():
    exportar_para_postgres()
    print("Processo concluído com sucesso.")

if __name__ == "__main__":
    ingestion()