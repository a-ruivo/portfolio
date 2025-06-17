import requests
import duckdb
import pandas as pd
import psycopg2
import json
import os
from dotenv import load_dotenv

# Caminho para o banco DuckDB
DUCKDB_PATH = "ibge_duckdb.db"

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

# URL da API
URL = "https://servicodados.ibge.gov.br/api/v3/agregados/1209/periodos/2000|2010|2022/variaveis/606?localidades=N3[all]&classificacao=58[all]"

def extrair_dados():
    print("[1/4] Extraindo dados da API IBGE...")
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao acessar API IBGE: {response.status_code}")

def normalize(json_data):
    print("[2/4] Normalizando estrutura JSON...")
    dados = pd.json_normalize(
        json_data,
        record_path=['resultados'],
        meta=['id', 'variavel', 'unidade']
    )
    dados1 = dados.explode('classificacoes').reset_index(drop=True)
    classificacoes_df = pd.json_normalize(dados1['classificacoes'])
    dados2 = dados.explode('series').reset_index(drop=True)
    serie_df = pd.json_normalize(dados2['series'])
    return pd.concat([dados1.drop(columns=['classificacoes']), classificacoes_df,dados2.drop(columns=['series']),serie_df], axis=1)

def criar_tabela_duckdb():
    print("[3/4] Criando tabela no banco DuckDB...")
    conn = duckdb.connect(DUCKDB_PATH)
    conn.execute("DROP TABLE IF EXISTS ibge_populacao")
    conn.execute("""
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
    conn.close()

def inserir_dados_duckdb(registros):
    print("[4/4] Inserindo dados no DuckDB...")
    conn = duckdb.connect(DUCKDB_PATH)
    conn.executemany(
        "INSERT INTO ibge_populacao (series, nome, categoria_0, categoria_1140, categoria_1141, categoria_1142, categoria_1143, categoria_2792, categoria_92982, categoria_1144, categoria_1145, categoria_3299, categoria_3300, categoria_3301, categoria_3520, categoria_3244, categoria_3245, classificacoes, localidade_id, localidade_nivel_id, localidade_nivel_nome, localidade_nome, serie_2000, serie_2010, serie_2022) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        registros
    )
    conn.close()

def extraction():
    json_data = extrair_dados()
    dados_norm = normalize(json_data)
    dados_norm = dados_norm.drop(columns=['id','variavel','unidade'])
    dados_norm.columns = [col.replace(".", "_") for col in dados_norm.columns]
    # Exporta para CSV local para inspeção opcional
    dados_norm.to_csv("populacao_ibge.csv", index=False)
    criar_tabela_duckdb()
    inserir_dados_duckdb(dados_norm[['series', 'nome', 'categoria_0', 'categoria_1140', 'categoria_1141', 'categoria_1142', 'categoria_1143', 'categoria_2792', 'categoria_92982', 'categoria_1144', 'categoria_1145', 'categoria_3299', 'categoria_3300', 'categoria_3301', 'categoria_3520', 'categoria_3244', 'categoria_3245', 'classificacoes', 'localidade_id', 'localidade_nivel_id', 'localidade_nivel_nome', 'localidade_nome', 'serie_2000', 'serie_2010', 'serie_2022']].itertuples(index=False, name=None))
    print("Tudo pronto! Os dados foram enviados com sucesso.")

if __name__ == "__main__":
    extraction()