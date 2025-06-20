#!/bin/bash

# =============================================================================
# Script de automação que atualiza a definição de um job no Jenkins a partir
# de um Jenkinsfile externo. Esse job aciona uma DAG no Apache Airflow por meio
# da API REST v2, utilizando autenticação via token.
# =============================================================================

# === Carrega variáveis do ambiente ===
set -a
source .env
set +a

# === Configurações ===
JENKINS_URL="http://localhost:8080"
JOB_NAME="pipeline_airflow_ibge"
JENKINSFILE_PATH="jenkinsfile"   # Caminho do Jenkinsfile separado
JENKINSFILE=$(<"$JENKINSFILE_PATH")

# === Obtém crumb CSRF do Jenkins ===
CRUMB_RESPONSE=$(curl -s -u "$JENKINS_USER:$JENKINS_TOKEN" "$JENKINS_URL/crumbIssuer/api/json")

# === Valida resposta do crumb ===
if [ -z "$CRUMB_RESPONSE" ] || ! echo "$CRUMB_RESPONSE" | jq -e .crumbRequestField > /dev/null; then
  echo "Erro: não foi possível obter o token CSRF do Jenkins. Verifique suas credenciais e a URL."
  exit 1
fi

# === Extrai nome e valor do crumb ===
CRUMB_FIELD=$(echo "$CRUMB_RESPONSE" | jq -r '.crumbRequestField')
CRUMB_TOKEN=$(echo "$CRUMB_RESPONSE" | jq -r '.crumb')

# === Gera XML da configuração do job dinamicamente ===
PIPELINE_XML=$(cat <<EOF
<flow-definition plugin="workflow-job">
  <description>Pipeline atualizado para Airflow 3 com API v2</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script><![CDATA[
$JENKINSFILE
    ]]></script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
</flow-definition>
EOF
)

# === Atualiza o job no Jenkins via API ===
echo "$PIPELINE_XML" | curl -s -o /dev/null -w "%{http_code}\n" \
  -X POST "$JENKINS_URL/job/$JOB_NAME/config.xml" \
  -u "$JENKINS_USER:$JENKINS_TOKEN" \
  -H "$CRUMB_FIELD: $CRUMB_TOKEN" \
  -H "Content-Type: application/xml" \
  --data-binary @- | {
    read STATUS
    if [ "$STATUS" -eq 200 ]; then
      echo "Job '$JOB_NAME' atualizado com sucesso."
    else
      echo "Erro ao atualizar o job '$JOB_NAME'. Código de resposta HTTP: $STATUS"
      exit 1
    fi
  }

# === Aciona a execução do job no Jenkins ===
BUILD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "$JENKINS_URL/job/$JOB_NAME/build" \
  -u "$JENKINS_USER:$JENKINS_TOKEN" \
  -H "$CRUMB_FIELD: $CRUMB_TOKEN")

if [ "$BUILD_STATUS" -eq 201 ]; then
  echo "Job '$JOB_NAME' iniciado com sucesso."
else
  echo "Erro ao iniciar o job '$JOB_NAME'. Código HTTP: $BUILD_STATUS"
  exit 1
fi
