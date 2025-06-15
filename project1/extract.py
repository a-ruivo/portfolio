import requests
import duckdb
import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Acessar credenciais
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
# Configuração do PostgreSQL
PG_CONFIG = {
    "dbname": db_name,
    "user": db_user,
    "password": db_password,
    "host": "localhost",
    "port": "5432"
}

# URL da API IBGE
URL = "https://servicodados.ibge.gov.br/api/v2/cnae/classes"

# Função para extrair os dados da API
def extrair_dados():
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao acessar API: {response.status_code}")
        return []

# Função para preparar os dados
def preparar_dados(dados):
    registros = []
    for item in dados:
        registros.append((item["id"], item["descricao"], ", ".join(item.get("observacoes", []))))
    return registros

# Criar banco DuckDB e tabela
def criar_tabela_duckdb():
    conn = duckdb.connect("cnae_duckdb.db")
    conn.execute("""DROP TABLE cnae""")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cnae (
            id INT NOT NULL,
            descricao  VARCHAR(100) NOT NULL,
            observacoes  VARCHAR(100) NOT NULL
        )
    """)
    conn.close()

# Inserir dados no DuckDB
def inserir_dados_duckdb(registros):
    conn = duckdb.connect("cnae_duckdb.db")
    conn.executemany("INSERT INTO cnae (id, descricao, observacoes) VALUES (?, ?, ?)", registros)
    conn.close()

# Exportar para PostgreSQL
def exportar_para_postgres():
    conn_duckdb = duckdb.connect("cnae_duckdb.db")
    conn_pg = psycopg2.connect(**PG_CONFIG)
    cursor_pg = conn_pg.cursor()

    dados = conn_duckdb.execute("SELECT * FROM cnae").fetchall()

    '''cursor_pg.execute("""
        CREATE TABLE IF NOT EXISTS cnae (
            id TEXT PRIMARY KEY,
            descricao TEXT,
            observacoes TEXT
        )
    """)'''

    cursor_pg.executemany("INSERT INTO cnae_classe (id, descricao, observacoes) VALUES (%s, %s, %s)", dados)

    conn_pg.commit()
    cursor_pg.close()
    conn_pg.close()
    conn_duckdb.close()

# Fluxo de execução
dados = extrair_dados()
if dados:
    registros = preparar_dados(dados)
    criar_tabela_duckdb()
    inserir_dados_duckdb(registros)
    exportar_para_postgres()
    print("Dados extraídos, processados e inseridos no PostgreSQL com sucesso!")
