from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

from kubernetes.client import models as k8s
from airflow.decorators import task


def show_envs():
    import time, os, datetime

    for item, value in os.environ.items():
        if "RUNTIME_ENV" in item:
            print('{}: {}'.format(item, value))
    time.sleep(20)


dag = DAG(dag_id='test_k8s_dag',
          description='test dag',
          schedule_interval=None,
          start_date=datetime(2017, 3, 20),
          catchup=False,
          )


pod_oveeride_config = {
    "pod_override": k8s.V1Pod(
        spec=k8s.V1PodSpec(
            containers=[
                k8s.V1Container(
                    name="base_container",  # base ??
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
                    env=[
                        k8s.V1EnvVar(
                            name="RUNTIME_ENV_" + field_path.replace(".", "_").upper(),
                            value_from=k8s.V1EnvVarSource(
                                field_ref=k8s.V1ObjectFieldSelector(
                                    field_path=field_path
                                )
                            )
                        ) for field_path in ["spec.nodeName",
                                             "metadata.name",
                                             "metadata.namespace",
                                             "status.podIP",
                                             "status.hostIP",
                                             ]
                    ]
                )
            ],
            tolerations=[
                k8s.V1Toleration(
                    effect="NoSchedule",
                    key="oos",
                    operator="Exists",
                )
            ],
            affinity=k8s.V1Affinity(
                node_affinity=k8s.V1NodeAffinity(
                    required_during_scheduling_ignored_during_execution=k8s.V1NodeSelector(
                        node_selector_terms=[
                            k8s.V1NodeSelectorTerm(
                                match_expressions=[
                                    k8s.V1NodeSelectorRequirement(
                                        key="team",
                                        operator="In",
                                        values=["oos"]
                                    )
                                ]
                            )
                        ]
                    )
                )
            )
        )
    ),
}


operators = []
for i in range(1, 6):
    operator = PythonOperator(task_id=f'pod_{i}{i}',
                              python_callable=show_envs,
                              dag=dag,
                              executor_config=pod_oveeride_config,
                              )
    operators.append(operator)

operators



