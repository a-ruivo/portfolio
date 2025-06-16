import requests
import duckdb
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

# Caminho para o banco DuckDB
DUCKDB_PATH = "populacao_duckdb.db"

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
URL = "https://servicodados.ibge.gov.br/api/v3/agregados/1288/periodos/1950|1960|1970|1980|1991|2000|2010/variaveis/606?localidades=N3[all]&classificacao=1[all]"

def extrair_dados():
    print("[1/6] Extraindo dados da API IBGE...")
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao acessar API IBGE: {response.status_code}")

def normalize(json_data):
    print("[2/6] Normalizando estrutura JSON...")
    dados = pd.json_normalize(
        json_data,
        record_path=['resultados'],
        meta=['id', 'variavel', 'unidade']
    )
    dados = dados.explode('classificacoes').reset_index(drop=True)
    classificacoes_df = pd.json_normalize(dados['classificacoes'])
    return pd.concat([dados.drop(columns=['classificacoes']), classificacoes_df], axis=1)

def formato_tabular(resultado):
    print("[3/6] Estruturando dados em formato tabular...")
    linha_list = []
    for _, row in resultado.iterrows():
        for item in row['series']:
            localidade = item['localidade']
            serie_anos = item['serie']

            categoria_dict = row.get('categoria', {})
            categoria_id = next(iter(categoria_dict), None)
            categoria_nome = categoria_dict.get(categoria_id) if categoria_id else None

            base_info = {
                'id': row['id'],
                'variavel': row['variavel'],
                'unidade': row['unidade'],
                'categoria_id': categoria_id,
                'categoria_nome': categoria_nome,
                'localidade_id': localidade['id'],
                'localidade_nome': localidade['nome'],
                'nivel_id': localidade['nivel']['id'],
                'nivel_nome': localidade['nivel']['nome']
            }

            for ano, valor in serie_anos.items():
                nova_linha = base_info.copy()
                nova_linha['ano'] = ano
                nova_linha['valor'] = int(valor.replace("-", "0"))
                linha_list.append(nova_linha)

    return pd.DataFrame(linha_list)

def criar_tabela_duckdb():
    print("[4/6] Criando tabela no banco DuckDB...")
    conn = duckdb.connect(DUCKDB_PATH)
    conn.execute("DROP TABLE IF EXISTS populacao")
    conn.execute("""
        CREATE TABLE populacao (
            localidade_nome VARCHAR,
            ano INT,
            valor INT
        )
    """)
    conn.close()

def inserir_dados_duckdb(registros):
    print("[5/6] Inserindo dados no DuckDB...")
    conn = duckdb.connect(DUCKDB_PATH)
    conn.executemany(
        "INSERT INTO populacao (localidade_nome, ano, valor) VALUES (?, ?, ?)",
        registros
    )
    conn.close()

def exportar_para_postgres():
    print("[6/6] Exportando dados para PostgreSQL...")
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

def pipeline():
    json_data = extrair_dados()
    dados_norm = normalize(json_data)
    df = formato_tabular(dados_norm)

    # Exporta para CSV local para inspeção opcional
    df.to_csv("populacao_ibge.csv", index=False)

    criar_tabela_duckdb()
    inserir_dados_duckdb(df[['localidade_nome', 'ano', 'valor']].itertuples(index=False, name=None))
    exportar_para_postgres()
    print("Tudo pronto! Os dados foram enviados com sucesso.")

if __name__ == "__main__":
    pipeline()