from datetime import datetime
from airflow import DAG
from airflow.providers.apache.hdfs.operators.hdfs import HdfsPutFileOperator
from airflow.providers.apache.hdfs.sensors.hdfs import HdfsSensor

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
}

with DAG(
    'hdfs_data_upload',
    default_args=default_args,
    schedule_interval=None,  # Manual trigger
    catchup=False,
) as dag:

    # Wait until HDFS is ready
    hdfs_sensor = HdfsSensor(
        task_id='check_hdfs_available',
        filepath='/',
        hdfs_conn_id='hdfs_default',
        timeout=60,
        poke_interval=10,
    )

    # Upload file task
    upload_task = HdfsPutFileOperator(
        task_id='upload_to_hdfs',
        local_file='/data/raw/yellow_tripdata.csv',
        remote_file='/user/abdulrehman/raw_data/yellow_tripdata.csv',
        hdfs_conn_id='hdfs_default',
    )

    hdfs_sensor >> upload_task