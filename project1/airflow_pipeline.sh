#!/bin/bash

# === Carrega variáveis do arquivo .env ===
set -a
source .env
set +a

# === CONFIGURAÇÕES ===
JENKINS_URL="http://localhost:8080"
JOB_NAME="pipeline_airflow_ibge"

# === Jenkinsfile embutido no script ===
JENKINSFILE=$(cat <<'EOF'
pipeline {
    agent any

    stages {
        stage('Obter token do Airflow') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'airflow-password-id',
                        usernameVariable: 'AIRFLOW_USER',
                        passwordVariable: 'AIRFLOW_PASS'
                    )
                ]) {
                    script {
                        def authResponse = httpRequest(
                            httpMode: 'POST',
                            url: 'http://localhost:9090/auth/token',
                            contentType: 'APPLICATION_JSON',
                            requestBody: """
{
  \"username\": \"${AIRFLOW_USER}\",
  \"password\": \"${AIRFLOW_PASS}\"
}
"""
                        )
                        def tokenJson = readJSON text: authResponse.content
                        env.AIRFLOW_TOKEN = tokenJson.token
                    }
                }
            }
        }

        stage('Acionar DAG') {
            steps {
                script {
                    def dagResponse = httpRequest(
                        httpMode: 'POST',
                        url: 'http://localhost:9090/api/v1/dags/pipeline_ibge/dagRuns',
                        customHeaders: [[name: 'Authorization', value: "Bearer ${env.AIRFLOW_TOKEN}"]],
                        contentType: 'APPLICATION_JSON',
                        requestBody: '{"conf": {}}'
                    )
                    echo "Airflow respondeu: ${dagResponse.status}"
                }
            }
        }
    }
}
EOF
)

# === Obtém crumb CSRF do Jenkins ===
read CRUMB_FIELD CRUMB_TOKEN <<< $(curl -s -u "$JENKINS_USER:$JENKINS_TOKEN" \
  "$JENKINS_URL/crumbIssuer/api/json" | jq -r '.crumbRequestField + " " + .crumb')

# === Cria o job via API ===
curl -X POST "$JENKINS_URL/createItem?name=$JOB_NAME" \
  -u "$JENKINS_USER:$JENKINS_TOKEN" \
  -H "$CRUMB_FIELD: $CRUMB_TOKEN" \
  -H "Content-Type: application/xml" \
  --data-binary @- <<EOF
<flow-definition plugin="workflow-job">
  <description>Pipeline criado via script com token</description>
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

echo
