from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),  # установите нужную дату старта
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'obsidian_manager',
    default_args=default_args,
    description='Запуск скрипта refresher.py',
    schedule_interval='1 * * * *',  # запуск каждый час на 1-й минуте
    catchup=False,
)

run_refresher = BashOperator(
    task_id='run_refresher',
    bash_command=(
        'cd "/Users/alextomtomo/Desktop/GitHub repo/Python/Obsidian_manager" && '
        '/Library/Frameworks/Python.framework/Versions/3.11/bin/python3 ./src/hour_manager/refresher.py >> /tmp/cron_logs.log 2>&1'
    ),
    dag=dag,
)
