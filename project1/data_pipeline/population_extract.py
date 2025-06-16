import requests
import duckdb
import pandas as pd
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
URL = "https://servicodados.ibge.gov.br/api/v3/agregados/1288/periodos/1950|1960|1970|1980|1991|2000|2010/variaveis/606?localidades=N3[all]&classificacao=1[all]"

# Função para extrair os dados da API
def extrair_dados():
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao acessar API: {response.status_code}")
        return []

# Criar banco DuckDB e tabela
def criar_tabela_duckdb():
    conn = duckdb.connect("population_duckdb.db")
    conn.execute("""DROP TABLE population""")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dados_ibge.population (
            localidade_nome VARCHAR,
            ano  INT,
            valor  INT
        )
    """)
    conn.close()

# Inserir dados no DuckDB
def inserir_dados_duckdb(registros):
    conn = duckdb.connect("populacao_duckdb.db")
    conn.executemany("INSERT INTO dados_ibge.populacao (localidade_nome, ano, valor) VALUES (?, ?, ?)", registros)
    conn.close()

# Exportar para PostgreSQL
def exportar_para_postgres():
    conn_duckdb = duckdb.connect("populacao_duckdb.db")
    conn_pg = psycopg2.connect(**PG_CONFIG)
    cursor_pg = conn_pg.cursor()

    dados = conn_duckdb.execute("SELECT * FROM populacao").fetchall()

    cursor_pg.execute("""
        CREATE TABLE IF NOT EXISTS populacao (
            location_name_str TEXT,
            year_num INT,
            population_qty INT
        )
    """)

    cursor_pg.executemany("INSERT INTO populacao (location_name_str, year_num, population_qty) VALUES (%s, %s, %s)", dados)

    conn_pg.commit()
    cursor_pg.close()
    conn_pg.close()
    conn_duckdb.close()

# Normalizando os dados
def normalize(json):
    dados = pd.json_normalize(
        json,
        record_path=['json'],
        meta=['id', 'variavel', 'unidade']
    ).explode('classificacoes').reset_index(drop=True).json_normalize(json['classificacoes'])
    return dados


# Limpa os dados
def limpeza(dados):
    resultado = pd.concat([dados.drop(columns=['classificacoes']), dados], axis=1)
    return resultado

# Lida com a lista 'series' e extrai informações tabulares
def formato_tabular(resultado):
    linha_list = []
    for _, row in resultado.iterrows():
        for item in row['series']:
            localidade = item['localidade']
            serie_anos = item['serie']
            
            # Trata categoria de forma segura
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
                nova_linha['valor'] = valor
                linha_list.append(nova_linha)
        df = pd.DataFrame(linha_list)
        return df

# Execução
    json = extrair_dados()
    normalize(json)
    limpeza()
    formato_tabular()
    criar_tabela_duckdb()
    inserir_dados_duckdb(df[['localidade_nome','ano','valor']])
    exportar_para_postgres()
    print("Dados extraídos, processados e inseridos no PostgreSQL com sucesso!")
