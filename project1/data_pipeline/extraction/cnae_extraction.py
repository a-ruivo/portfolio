import requests
import duckdb
import psycopg2
import os
from dotenv import load_dotenv

DUCKDB_PATH = "cnae_duckdb.db"

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

URL = "https://servicodados.ibge.gov.br/api/v2/cnae/classes"

def extrair_dados():
    print("1/5 - Extraindo dados da API CNAE")
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao acessar API: {response.status_code}")

def preparar_dados(dados):
    print("2/5 - Preparando os dados")
    registros = []
    for item in dados:
        registros.append((
            int(item["id"]),
            item["descricao"],
            ", ".join(item.get("observacoes", []))
        ))
    return registros

def criar_tabela_duckdb():
    print("3/5 - Criando tabela DuckDB")
    conn = duckdb.connect(DUCKDB_PATH)
    conn.execute("DROP TABLE IF EXISTS cnae")
    conn.execute("""
        CREATE TABLE cnae (
            id INT PRIMARY KEY,
            descricao VARCHAR,
            observacoes VARCHAR
        )
    """)
    conn.close()

def inserir_dados_duckdb(registros):
    print("4/5 - Inserindo dados no DuckDB")
    conn = duckdb.connect(DUCKDB_PATH)
    conn.executemany(
        "INSERT INTO cnae (id, descricao, observacoes) VALUES (?, ?, ?)",
        registros
    )
    conn.close()

def exportar_para_postgres():
    print("5/5 - Exportando dados para PostgreSQL")
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

def pipeline():
    dados = extrair_dados()
    registros = preparar_dados(dados)
    criar_tabela_duckdb()
    inserir_dados_duckdb(registros)
    exportar_para_postgres()
    print("Processo concluído com sucesso.")

if __name__ == "__main__":
    pipeline()