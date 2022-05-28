from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

from kubernetes.client import models as k8s
from airflow.decorators import task

def print_hello():
    import time
    import os
    import datetime
    for item, value in os.environ.items():
        print('{}: {}'.format(item, value))

    time.sleep(20)
    print("hello")


dag = DAG(dag_id='hello_world_dag2',
          description='Hello World DAG',
          schedule_interval=None,
          start_date=datetime(2017, 3, 20),
          catchup=False,
          )

tolerations = [{
    'key': 'oos',
    'operator': 'Exists',
    #'value': 'true'
}]
kubernetes_executor = {
    "KubernetesExecutor": {
        "request_cpu": "500m",
        "request_memory": "512Mi",
        "limit_cpu": "500m",
        "limit_memory": "512Mi",
        "tolerations": tolerations,
    }
}

hello_operator = PythonOperator(task_id='hello_task',
                                python_callable=print_hello,
                                dag=dag,
                                executor_config=kubernetes_executor,
                                )


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
            tolerations=[
                k8s.V1Toleration(
                    effect="NoSchedule",
                    key="oos",
                    operator="Exists",
                )
            ]
        )

    ),
}
#
# @task(executor_config=executor_config_volume_mount)

def task_with_template():
    print_hello()


template_operator = PythonOperator(task_id='task_with_template',
                                   python_callable=task_with_template,
                                   dag=dag,
                                   executor_config=executor_config_volume_mount
                                   )


hello_operator >> template_operator