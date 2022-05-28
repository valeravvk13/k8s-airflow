from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

def print_hello():
    import time
    time.sleep(20)
    return 'Hello world from first Airflow DAG!'

dag = DAG(dag_id='hello_world_dag3',
          description='Hello World DAG',
          schedule_interval=None,
          start_date=datetime(2017, 3, 20),
          catchup=False,
          )

hello_operator = PythonOperator(task_id='hello_task', python_callable=print_hello, dag=dag)
hello_operator2 = PythonOperator(task_id='hello_task2', python_callable=print_hello, dag=dag)
hello_operator >> hello_operator2