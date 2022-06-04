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

print("sfgs.sadfgs".replace(".", "_").upper())


def show_envs(sleep_time=10):
    import time, os, datetime

    for item, value in os.environ.items():
        if ("RUNTIME_ENV" in item) | ("IS_TESTING_" in item):
            print('{}: {}'.format(item, value))

    print(f"sleep_time: {sleep_time}")
    if (sleep_time is None):
        sleep_time = 10
    time.sleep(sleep_time)


show_envs()
