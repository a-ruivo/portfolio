#!/bin/bash

# === Carrega variáveis do ambiente ===
set -a
source .env
set +a

# === Configurações ===
JENKINS_URL="http://localhost:8081"
JOB_NAME="pipeline_airflow_ibge"
JENKINSFILE_PATH="jenkinsfile"
JENKINSFILE=$(<"$JENKINSFILE_PATH")

# === Obtém crumb CSRF ===
CRUMB_RESPONSE=$(curl -s -u "$JENKINS_USER:$JENKINS_TOKEN" "$JENKINS_URL/crumbIssuer/api/json")
CRUMB_FIELD=$(echo "$CRUMB_RESPONSE" | jq -r '.crumbRequestField')
CRUMB_TOKEN=$(echo "$CRUMB_RESPONSE" | jq -r '.crumb')

# === Gera XML do pipeline ===
PIPELINE_XML=$(cat <<EOF
<flow-definition plugin="workflow-job">
  <description>Pipeline atualizado para Airflow com API</description>
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

# === Verifica se o job já existe ===
EXISTE=$(curl -s -o /dev/null -w "%{http_code}" \
  -u "$JENKINS_USER:$JENKINS_TOKEN" \
  "$JENKINS_URL/job/$JOB_NAME/api/json")

if [ "$EXISTE" -eq 200 ]; then
  echo "🔄 Job '$JOB_NAME' já existe. Atualizando configuração..."
  echo "$PIPELINE_XML" | curl -s -o /dev/null \
    -X POST "$JENKINS_URL/job/$JOB_NAME/config.xml" \
    -u "$JENKINS_USER:$JENKINS_TOKEN" \
    -H "$CRUMB_FIELD: $CRUMB_TOKEN" \
    -H "Content-Type: application/xml" \
    --data-binary @-
else
  echo "🆕 Job '$JOB_NAME' não existe. Criando novo job..."
  echo "$PIPELINE_XML" | curl -s -o /dev/null \
    -X POST "$JENKINS_URL/createItem?name=$JOB_NAME" \
    -u "$JENKINS_USER:$JENKINS_TOKEN" \
    -H "$CRUMB_FIELD: $CRUMB_TOKEN" \
    -H "Content-Type: application/xml" \
    --data-binary @-
fi

# === Aciona o build ===
BUILD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "$JENKINS_URL/job/$JOB_NAME/build" \
  -u "$JENKINS_USER:$JENKINS_TOKEN" \
  -H "$CRUMB_FIELD: $CRUMB_TOKEN")

if [ "$BUILD_STATUS" -eq 201 ]; then
  echo "🚀 Job '$JOB_NAME' iniciado com sucesso."
else
  echo "❌ Erro ao iniciar o job '$JOB_NAME'. Código HTTP: $BUILD_STATUS"
  exit 1
fi
