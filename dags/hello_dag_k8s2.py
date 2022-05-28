from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

from kubernetes.client import models as k8s
from airflow.decorators import task

def print_hello():
    import time
    time.sleep(120)
    return 'hello!'

dag = DAG(dag_id='hello_world_dag2',
          description='Hello World DAG',
          schedule_interval=None,
          start_date=datetime(2017, 3, 20),
          catchup=False,
          )

# hello_operator = PythonOperator(task_id='hello_task',
#                                 python_callable=print_hello,
#                                 dag=dag,
#                                 executor_config={
#                                     "KubernetesExecutor":
#                                         {"request_memory": "1GB",
#                                          "limit_memory": "2GB",
#                                          },
#                                 }
#                                 )


executor_config_volume_mount = {
    "pod_override": k8s.V1Pod(
        spec=k8s.V1PodSpec(
            containers=[
                k8s.V1Container(
                    name="base_container",
                    resources=k8s.V1ResourceRequirements(
                        limits={
                            "cpu": "500m",
                            "memory": "512Mi",
                        },
                        requests={
                            "cpu": "500m",
                            "memory": "512Mi",
                        },
                    ),
                )
            ],
        )

    ),
}
#
# @task(executor_config=executor_config_volume_mount)

def task_with_template():
    import time
    time.sleep(120)
    return 'hello!'


template_operator = PythonOperator(task_id='task_with_template',
                                   python_callable=task_with_template,
                                   dag=dag,
                                   executor_config=executor_config_volume_mount
                                   )


template_operator