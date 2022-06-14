from datetime import datetime
import json
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

from kubernetes.client import models as k8s
from airflow.models import Variable


def show_envs(kubernetes_executor, sleep_time=10,):
    import time, os, datetime

    for item, value in os.environ.items():
        if ("RUNTIME_ENV" in item) | ("IS_TESTING_" in item):
            print('{}: {}'.format(item, value))

    print(f"sleep_time: {sleep_time}")
    if (sleep_time is None) | (sleep_time == "None"):
        sleep_time = 20

    print(kubernetes_executor)

    import config_dir
    print(config_dir.main_hdfs_path)
    print(config_dir.prod_hdfs_path)
    print(config_dir.data_dir_path)
    print(config_dir.prices_path)
    print(config_dir.promo_info_path)

    time.sleep(int(sleep_time))


dag = DAG(dag_id='kubernetes_executor_dag',
          description='kuber executor dag',
          schedule_interval=None,
          start_date=datetime(2017, 3, 20),
          catchup=False,
          )


kubernetes_executor = {
    "KubernetesExecutor": {
        "volumes": [
            {
                "name": "hadoop-credentials",
                "secret": {"secretName": "user-tsx"},
            },
        ],
        "request_cpu": "250m",
        "request_memory": "256Mi",
        "limit_cpu": "500m",
        "limit_memory": "512Mi",
        "envs": [
            {'name': 'IS_TESTING_OOS_ONLINE_FEATURES', 'value': 'OOS_TEST_TRUE'}
        ] + [
            {'name': "RUNTIME_ENV_" + field_path.replace(".", "_").upper(),
             'value': field_path
             }
            for field_path in [
                "spec.nodeName",
                "metadata.name",
                "metadata.namespace",
                "status.podIP",
                "status.hostIP",
            ]
        ],
        "tolerations": [
            {'effect': 'NoSchedule',
             'key': 'oos',
             'operator': 'Exists',
             }
        ],
        "affinity": {
            'node_affinity': {
                'required_during_scheduling_ignored_during_execution': {
                    'node_selector_terms': [
                        {'match_expressions': [
                            {'key': 'team',
                             'operator': 'In',
                             'values': ['oos']
                             }
                        ],
                        }
                    ]
                }
            }
        },
    }
}


executor_config = kubernetes_executor
var_executor_config = Variable.get("kubernetes_executor_bdsd_8115")
if var_executor_config != "{}":
    executor_config = eval(var_executor_config)


operators = []
for i in range(1, 4):
    operator = PythonOperator(task_id=f'pod_{i}{i}',
                              python_callable=show_envs,
                              dag=dag,
                              op_kwargs={
                                  'sleep_time': "{{ dag_run.conf.get('sleep_time') }}",
                                  'kubernetes_executor': executor_config,
                              },
                              executor_config=executor_config,
                              )
    operators.append(operator)

operators
