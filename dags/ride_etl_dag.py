from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator  # type: ignore
from airflow.operators.python_operator import PythonOperator  # type: ignore

default_args={
    "owner":"rideflow",
    "start_date":datetime.today(),
    "retries":1,
    "retry_delay": timedelta(minutes=5)
}

def run_spark_job():
    import subprocess
    subprocess.run(["spark-submit", "/app/spark_jobs/raw_to_silver.py"], check=True)


with DAG(
    dag_id="ride_etl_dag",
    default_args=default_args,
    description="ETL DAG for NYC Taxi Data",
    schedule_interval="@daily",
    catchup=False,
    tags=["rideflow", "nyc_taxi"],
) as dag:

    run_spark_job_task = PythonOperator(
        task_id="run_spark_job",
        python_callable=run_spark_job
    )