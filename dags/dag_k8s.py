from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

from kubernetes.client import models as k8s
from airflow.decorators import task


def print_hello():
    import time, os, datetime

    for item, value in os.environ.items():
        print('{}: {}'.format(item, value))
    time.sleep(20)
    print("hello")


dag = DAG(dag_id='k8s-taint-dag',
          description='test taint dag',
          schedule_interval=None,
          start_date=datetime(2017, 3, 20),
          catchup=False,
          )

resources = {
    "request_cpu": "200m",
    "request_memory": "256Mi",
    "limit_cpu": "200m",
    "limit_memory": "256Mi",
}
tolerations = {
    "tolerations": [
        {
            'key': 'oos',
            'operator': 'Exists',
        }
    ]
}
affinity = {
    "affinity": {
        'node_affinity': {
            'preferred_during_scheduling_ignored_during_execution': None,
            'required_during_scheduling_ignored_during_execution': {
                'node_selector_terms': [
                    {
                        'match_expressions': [
                            {
                                'key': 'team',
                                'operator': 'In',
                                'values': ['oos']
                            }
                        ],
                        'match_fields': None
                    }
                ]
            }
        },
        'pod_affinity': None,
        'pod_anti_affinity': None
    }
}



simple_operator = PythonOperator(task_id='pod_simple',
                                python_callable=print_hello,
                                dag=dag,
                                executor_config={
                                    "KubernetesExecutor": {
                                        **resources,
                                    }
                                },
                                )


affinity_operator = PythonOperator(task_id='pod_affinity',
                                   python_callable=print_hello,
                                   dag=dag,
                                   executor_config={
                                       "KubernetesExecutor": {
                                           **resources,
                                           **affinity,
                                       }
                                   },
                                   )

affinity_tolerations_operator = PythonOperator(task_id='pod_affinity_tolerations',
                                               python_callable=print_hello,
                                               dag=dag,
                                               executor_config={
                                                   "KubernetesExecutor": {
                                                       **resources,
                                                       **tolerations,
                                                       **affinity,
                                                   }
                                               },
                                               )



executor_config_pod_override_template = {
    "pod_override": k8s.V1Pod(
        spec=k8s.V1PodSpec(
            containers=[
                k8s.V1Container(
                    name="base_container",
                    resources=k8s.V1ResourceRequirements(
                        limits={
                            "cpu": "200m",
                            "memory": "256Mi",
                        },
                        requests={
                            "cpu": "200m",
                            "memory": "256Mi",
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

template_operator = PythonOperator(task_id='template_pod_override',
                                   python_callable=print_hello,
                                   dag=dag,
                                   executor_config=executor_config_pod_override_template
                                   )


[simple_operator, affinity_operator, affinity_tolerations_operator, template_operator]


