# arquivo: pipeline_ibge_dag_airflow.py

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

with DAG(
    dag_id="pipeline_ibge_dag_airflow",
    start_date=datetime(2023, 1, 1),
    schedule=timedelta(days=1),
    catchup=False,
    tags=["ibge", "exemplo"],
) as dag:

    exemplo = BashOperator(
        task_id="tarefa_exemplo",
        bash_command='echo "DAG carregada com sucesso!"',
    )
