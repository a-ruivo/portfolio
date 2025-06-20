#!/bin/bash

# === Carrega variáveis do arquivo .env ===
set -a
source .env
set +a

# === CONFIGURAÇÕES ===
JENKINS_URL="http://localhost:8080"
JOB_NAME="pipeline_airflow_ibge"

# === Jenkinsfile embutido no script (adaptado p/ API v2 e logical_date) ===
JENKINSFILE=$(cat <<'EOF'
pipeline {
    agent any

    stages {
        stage('Acionar DAG no Airflow') {
            steps {
                withCredentials([
                    string(credentialsId: 'airflow-static-token', variable: 'AIRFLOW_TOKEN')
                ]) {
                    script {
                        def logicalDate = new Date().format("yyyy-MM-dd'T'HH:mm:ss'Z'", TimeZone.getTimeZone("UTC"))


                        def payload = groovy.json.JsonOutput.toJson([
                            conf: [:],
                            logical_date: logicalDate
                        ])

                        def dagResponse = httpRequest(
                            httpMode: 'POST',
                            url: 'http://localhost:9090/api/v2/dags/pipeline_ibge/dagRuns',
                            customHeaders: [[name: 'Authorization', value: "Bearer ${AIRFLOW_TOKEN}"]],
                            contentType: 'APPLICATION_JSON',
                            requestBody: payload,
                            validResponseCodes: '100:599'
                        )

                        echo "DAG acionada! Código de resposta: ${dagResponse.status}"
                        echo "Corpo da resposta: ${dagResponse.content}"
                    }
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

# === Atualiza job existente com novo Jenkinsfile ===
curl -X POST "$JENKINS_URL/job/$JOB_NAME/config.xml" \
  -u "$JENKINS_USER:$JENKINS_TOKEN" \
  -H "$CRUMB_FIELD: $CRUMB_TOKEN" \
  -H "Content-Type: application/xml" \
  --data-binary @- <<EOF
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
