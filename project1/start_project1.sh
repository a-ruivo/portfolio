#!/bin/bash

COMPOSE_PATH="/home/ruivo/analytics_engineer/portfolio/project1/infra/docker/docker_compose.yml"
TERRAFORM_PATH="/home/ruivo/analytics_engineer/portfolio/project1/infra/terraform"

# Carrega variáveis do .env
set -o allexport
source .env
set +o allexport

echo ""
read -p "Deseja provisionar a EC2 com Terraform agora? (s/n): " resposta

if [[ "$resposta" == "s" || "$resposta" == "S" ]]; then
    echo "Efetuando login via AWS SSO..."
  aws sso login --profile default || {
    echo "Falha no login via AWS SSO. Verifique suas configurações no ~/.aws/config."
    exit 1
  }
  
  cd "$TERRAFORM_PATH" || { echo "Diretório Terraform não encontrado."; exit 1; }

  echo "Inicializando Terraform..."
  terraform init

  cd "$TERRAFORM_PATH"

  echo "Validando plano de execução..."
  terraform plan

  echo ""
  read -p "Deseja aplicar o plano e criar a EC2? (s/n): " aplicar

  if [[ "$aplicar" == "s" || "$aplicar" == "S" ]]; then
    cd "$TERRAFORM_PATH"
    terraform apply
  else
    echo "Criação da EC2 cancelada pelo usuário."
  fi

  cd ..
else
  echo "Etapa Terraform pulada."
fi

echo "Extraindo IP da EC2..."
cd "$TERRAFORM_PATH"
terraform refresh
EC2_IP=$(terraform output -raw ec2_public_ip)

if [[ -z "$EC2_IP" ]]; then
  echo "IP não encontrado. Verifique o estado do Terraform."
  exit 1
fi

echo "Atualizando .env com IP: $EC2_IP"
ENV_PATH="/home/ruivo/analytics_engineer/portfolio/project1/.env"

# Substitui ou adiciona a variável DB_HOST de forma segura
grep -v "^DB_HOST=" "$ENV_PATH" > "$ENV_PATH.tmp"
echo "DB_HOST=$EC2_IP" >> "$ENV_PATH.tmp"
mv "$ENV_PATH.tmp" "$ENV_PATH"


echo "Limpando containers anteriores..."
docker compose -f "$COMPOSE_PATH" down -v

echo "Subindo ambiente Airflow + Jenkins..."

echo "Subindo o PostgreSQL..."
docker compose -f "$COMPOSE_PATH" up -d postgres

echo "Subindo o Jenkins..."
docker compose -f "$COMPOSE_PATH" up -d jenkins

echo "Inicializando banco de dados do Airflow..."
docker compose -f "$COMPOSE_PATH" run --rm airflow-init

echo "Criando usuário administrador no Airflow..."
docker compose -f "$COMPOSE_PATH" run --rm airflow-webserver airflow users create \
  --username "$AIRFLOW_ADMIN_USERNAME" \
  --firstname "$AIRFLOW_ADMIN_FIRSTNAME" \
  --lastname "$AIRFLOW_ADMIN_LASTNAME" \
  --role Admin \
  --email "$AIRFLOW_ADMIN_EMAIL" \
  --password "$AIRFLOW_ADMIN_PASSWORD"

echo "Subindo webserver e scheduler do Airflow..."
docker compose -f "$COMPOSE_PATH" up -d airflow-webserver airflow-scheduler

echo "Verificando se a pasta de DAGs está sendo montada corretamente..."
docker compose -f "$COMPOSE_PATH" exec airflow-webserver ls /opt/airflow/project1/dags

echo "Airflow: http://localhost:8080"
echo "Jenkins: http://localhost:8081"



