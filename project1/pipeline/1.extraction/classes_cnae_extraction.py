import requests
import duckdb
import psycopg2
import os
from dotenv import load_dotenv

DUCKDB_PATH = "ibge_duckdb.db"

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
    print("1/4 - Extraindo dados da API CNAE")
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao acessar API: {response.status_code}")

def preparar_dados(dados):
    print("2/4 - Preparando os dados")
    registros = []
    for item in dados:
        registros.append((
            int(item["id"]),
            item["descricao"],
            ", ".join(item.get("observacoes", []))
        ))
    return registros

def criar_tabela_duckdb():
    print("3/4 - Criando tabela DuckDB")
    conn = duckdb.connect(DUCKDB_PATH)
    conn.execute("DROP TABLE IF EXISTS ibge_classes_cnae")
    conn.execute("""
        CREATE TABLE ibge_classes_cnae (
            id INT PRIMARY KEY,
            descricao VARCHAR,
            observacoes VARCHAR
        )
    """)
    conn.close()

def inserir_dados_duckdb(registros):
    print("4/4 - Inserindo dados no DuckDB")
    conn = duckdb.connect(DUCKDB_PATH)
    conn.executemany(
        "INSERT INTO ibge_classes_cnae (id, descricao, observacoes) VALUES (?, ?, ?)",
        registros
    )
    conn.close()

def extraction():
    dados = extrair_dados()
    registros = preparar_dados(dados)
    criar_tabela_duckdb()
    inserir_dados_duckdb(registros)
    print("Processo concluído com sucesso.")

if __name__ == "__main__":
    extraction()