# ============================================================================
# DAG para orquestrar um pipeline com 4 etapas: extração, ingestão,
# transformação e publicação de dados populacionais.
# Cada etapa é executada via BashOperator para manter os imports fora do DAG.
# ============================================================================

from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow import DAG
from datetime import datetime, timedelta

BASE_PATH = "/opt/airflow/pipeline"

default_args = {
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
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

transform = BashOperator(
    task_id="transform_population",
    bash_command=f"bash {BASE_PATH}/3.transformation/dbt_project1/run_dbt.sh",
    dag=dag,
)

service1 = BashOperator(
    task_id="service_streamlit",
    bash_command=f"python {BASE_PATH}/4.service/dbt_project1/app.py",
    dag=dag,
)

extract >> ingest >> transform >> service1
