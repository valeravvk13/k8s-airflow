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

print(k8s.V1Toleration(effect="NoSchedule", key="oos", operator="Exists",).to_dict())

print(pod.to_dict())
print(pod.to_str())