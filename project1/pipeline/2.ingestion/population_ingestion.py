import duckdb
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

SHARED_PATH = "/opt/airflow/shared_data"
DUCKDB_PATH = os.path.join(SHARED_PATH, "ibge_duckdb.db")

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

def export_to_postgres():
    print("Exporting data from DuckDB to PostgreSQL...")

    # Connect to DuckDB and fetch simplified data
    conn_duckdb = duckdb.connect(DUCKDB_PATH)
    query = "SELECT nome, grupo_idade, localidade, serie_2000, serie_2010, serie_2022 FROM ibge_populacao_etaria"
    dados = conn_duckdb.execute(query).fetchall()

    # Connect to PostgreSQL
    conn_pg = psycopg2.connect(**PG_CONFIG)
    cursor_pg = conn_pg.cursor()

    cursor_pg.execute("DROP TABLE IF EXISTS silver.ibge_populacao_etaria;")
    cursor_pg.execute("""
        CREATE TABLE silver.ibge_populacao_etaria (
            nome VARCHAR,
            grupo_idade VARCHAR,
            localidade VARCHAR,
            serie_2000 VARCHAR,
            serie_2010 VARCHAR,
            serie_2022 VARCHAR
        );
    """)

    for row in dados:
        try:
            cursor_pg.execute("""
                INSERT INTO silver.ibge_populacao_etaria 
                (nome, grupo_idade, localidade, serie_2000, serie_2010, serie_2022)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, row)
        except Exception as e:
            print("Error inserting row:", row, e)

    conn_pg.commit()
    cursor_pg.close()
    conn_pg.close()
    conn_duckdb.close()

def ingestion():
    export_to_postgres()
    print("Done! Data successfully exported to PostgreSQL.")

if __name__ == "__main__":
    ingestion()