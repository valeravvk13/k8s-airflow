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

print(pod.to_str())

affinity = {
    "affinity": {
        'node_affinity': {
            'required_during_scheduling_ignored_during_execution': {
                'node_selector_terms': [
                    {'key': 'team',
                     'operator': 'In',
                     'values': ['oos']
                     }
                ]
            }
        }
    }
}
print({**affinity})