from kubernetes.client import models as k8s

pod = k8s.V1Affinity(
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

#print(k8s.V1Toleration(effect="NoSchedule", key="oos", operator="Exists",).to_dict())

# pod = k8s.V1Volume(
#                         name="hadoop-credentials",
#                         secret=k8s.V1SecretVolumeSource(
#                             secret_name="user-nlfs",
#                         )
#                     )
# #print(pod.to_dict())
# print(pod.to_str())


k8s.V1EnvVar(
    name="env_prefix" + "",
    value_from=k8s.V1EnvVarSource(
        field_ref=k8s.V1ObjectFieldSelector(
            field_path="requests.cpu"
        )
    )
)


pod = k8s.V1Pod(
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
    )



def delete_none(_dict):
    """Delete None values recursively from all of the dictionaries"""
    for key, value in list(_dict.items()):
        if isinstance(value, dict):
            delete_none(value)
        elif value is None:
            del _dict[key]
        elif isinstance(value, list):
            for v_i in value:
                if isinstance(v_i, dict):
                    delete_none(v_i)

    return _dict

filtered_dict = delete_none(pod.to_dict())
filtered_dict = {"pod_override": filtered_dict}
import json
str_pod = json.dumps(filtered_dict)

with open("pod_over.txt", "w") as file:
    file.write(str_pod)
#
# with open("pod_over.txt", "r") as file:
#     print(file.readline())
#print(str_pod)

