# ============================================================================
# DAG para orquestrar um pipeline com 4 etapas: extração, ingestão,
# transformação e publicação de dados populacionais.
# Cada etapa é executada via BashOperator para manter os imports fora do DAG.
# ============================================================================

from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow import DAG
from docker.types import Mount
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

BASE_PATH = "/opt/airflow/project1/pipeline"

default_args = {
    'start_date': datetime(2025, 1, 1),
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id="pipeline_ibge_dag_airflow",
    default_args=default_args,
    schedule=timedelta(days=1),
    catchup=False,
)

extract = BashOperator(
    task_id="extract_population",
    bash_command=f"python {BASE_PATH}/1.extraction/population_extraction.py",
    dag=dag,
)

ingest = BashOperator(
    task_id="ingest_population",
    bash_command=f"python {BASE_PATH}/2.ingestion/population_ingestion.py",
    dag=dag,
)

from docker.types import Mount

transform = DockerOperator(
    task_id="transform_population",
    image="ghcr.io/dbt-labs/dbt-postgres:1.10.1",
    api_version="auto",
    auto_remove=True,
    command="run",
    docker_url="unix://var/run/docker.sock",
    environment={"DB_HOST": os.getenv("DB_HOST")},
    network_mode="bridge",
    mounts=[
        Mount(source="/home/ruivo/.dbt", target="/root/.dbt", type="bind"),
    ],
    working_dir="/root",
    dag=dag,
)

service1 = BashOperator(
    task_id="service_streamlit",
    bash_command=f"python {BASE_PATH}/4.service/dbt_project1/app.py",
    dag=dag,
)

extract >> ingest >> transform >> service1
