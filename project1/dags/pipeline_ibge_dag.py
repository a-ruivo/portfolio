from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import subprocess

BASE_PATH = "/home/ruivo/analytics_engineer/portfolio/project1/pipeline"

def run_script(path):
    subprocess.run(["python", path], check=True)

with DAG(
    dag_id="pipeline_ibge",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    extract = PythonOperator(
        task_id="extract_population",
        python_callable=lambda: run_script(f"{BASE_PATH}/1.extraction/population_extraction.py")
    )

    ingest = PythonOperator(
        task_id="ingest_population",
        python_callable=lambda: run_script(f"{BASE_PATH}/2.ingestion/population_ingestion.py")
    )

    transform = PythonOperator(
        task_id="transform_population",
        python_callable=lambda: run_script(f"{BASE_PATH}/3.transformation/dbt_project1/run_dbt.sh")
    )

    service1 = PythonOperator(
        task_id="service_streamlit",
        python_callable=lambda: run_script(f"{BASE_PATH}/4.service/dbt_project1/app.py")
    )

    extract >> ingest >> transform >> service1
