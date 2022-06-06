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

    time.sleep(int(sleep_time))


dag = DAG(dag_id='test_k8s_dag',
          description='test dag',
          schedule_interval=None,
          start_date=datetime(2017, 3, 20),
          catchup=False,
          )


pod_override_tmpl = {
    "pod_override": k8s.V1Pod(
        spec=k8s.V1PodSpec(
            containers=[
                k8s.V1Container(
                    name="base",
                    # resources=k8s.V1ResourceRequirements(
                    #     limits={
                    #         "cpu": "10000m",  # "72000m"
                    #         "memory": "10Gi",  # "503Gi"
                    #     },
                    #     requests={
                    #         "cpu": "8192m",
                    #         "memory": "8Gi",
                    #     },
                    # ),
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
                    ] + [
                        k8s.V1EnvVar(name="IS_TESTING_OOS_ONLINE_FEATURES", value="OOS_TEST_TRUE")
                    ],
                ),
            ],
            volumes=[
                k8s.V1Volume(
                    name="hadoop-credentials",
                    secret=k8s.V1SecretVolumeSource(
                        secret_name="user-tsx",
                    )
                ),
            ],
            tolerations=[
                k8s.V1Toleration(
                    effect="NoSchedule",
                    key="oos",
                    operator="Exists",
                ),
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
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ),
        ),

    ),
}

executor_config = pod_override_tmpl
var_executor_config = Variable.get("executor_config_bdsd_8115")
if var_executor_config != "{}":
    executor_config = eval(var_executor_config)


# pod_config = json.loads(Variable.get("pod_config"))
# print(f"in logs: {pod_config}, {type(pod_config)}")

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



