FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y build-essential git

# Cria diretório de trabalho
WORKDIR /dbt

# Copia o requirements.txt e instala pacotes
COPY requirements_dbt.txt .
RUN pip install --no-cache-dir -r requirements_dbt.txt

# Copia o projeto dbt
COPY . .

ENTRYPOINT ["dbt"]
