import time
import os
from typing import Dict, List
from uuid import uuid4

from kubernetes import client as k8s_client


def check_dependent_pods(
    namespace: str,
    name: str = None,
    statuses: List[str] = None,
    labels: Dict[str, str] = None,
):
    assert (name or labels) is not None, "must specify pod name or label selector"

    if statuses is None:
        statuses = ["Running", "Succeeded"]

    api = k8s_client.CoreV1Api()

    if name is not None:
        pods = [api.read_namespaced_pod(namespace=namespace, name=name)]
    else:
        label_selector_string = ",".join(
            f"{key}={value}" for key, value in labels.items()
        )

        pods = api.list_namespaced_pod(
            namespace=namespace, label_selector=label_selector_string
        ).items

    for pod in pods:
        status = pod.status.phase

        if status not in statuses:
            raise RuntimeError(
                f"pod '{pod.metadata.name}' has status of '{status}', expecting to be in {', '.join(statuses)}"
            )


def run_pod_to_completion(namespace: str, body: k8s_client.V1Pod) -> k8s_client.V1Pod:
    pod_name = body.metadata.name
    api = k8s_client.CoreV1Api()

    api.create_namespaced_pod(namespace=namespace, body=body)
    pod = api.read_namespaced_pod(namespace=namespace, name=pod_name)

    while pod.status.phase not in ["Succeeded", "Failed"]:
        pod = api.read_namespaced_pod(namespace=namespace, name=pod_name)
        time.sleep(3)

    if pod.status.phase == "Failed":
        raise RuntimeError(f"Test engine pod failed (pod: {pod_name})")

    return pod


def run_io_utility(
    test_engine_name: str,
    namespace: str,
    pvc_name: str,
    io_config: Dict[str, str],
    transfer_path: str,
):
    io_utility_name = f"{test_engine_name}-io-utility-{str(uuid4())[:8]}"

    volume = k8s_client.V1Volume(
        name=pvc_name,
        persistent_volume_claim=k8s_client.V1PersistentVolumeClaimVolumeSource(
            claim_name=pvc_name
        ),
    )

    volume_mount = k8s_client.V1VolumeMount(
        name=pvc_name, mount_path=os.path.join("/", pvc_name)
    )

    pod_env = [
        k8s_client.V1EnvVar(name=key, value=value) for key, value in io_config.items()
    ]

    # NOTE: specify service account?
    pod_body = k8s_client.V1Pod(
        metadata=k8s_client.V1ObjectMeta(
            name=io_utility_name,
            labels={
                "run_id": test_engine_name,
                "run": io_utility_name,
                "family": "cicada",
                "type": "cicada-io-utility",
            },
        ),
        spec=k8s_client.V1PodSpec(
            restart_policy="Never",
            containers=[
                k8s_client.V1Container(
                    image="cicadatesting/cicada-operator-io-utility:latest",
                    name=io_utility_name,
                    volume_mounts=[volume_mount],
                    env=pod_env,
                    args=["transfer", transfer_path],
                )
            ],
            volumes=[volume],
        ),
    )

    return run_pod_to_completion(namespace, pod_body)


def run_engine(
    test_engine_name: str,
    namespace: str,
    tests_pvc: str,
    reports_pvc: str,
    tests_mount_path: str = None,
    reports_mount_path: str = None,
    engine_service_account: str = None,
    engine_config: Dict[str, str] = None,
):
    tests_volume = k8s_client.V1Volume(
        name=tests_pvc,
        persistent_volume_claim=k8s_client.V1PersistentVolumeClaimVolumeSource(
            claim_name=tests_pvc
        ),
    )

    tests_volume_mount = k8s_client.V1VolumeMount(
        name=tests_pvc, mount_path=os.path.join("/", tests_mount_path)
    )

    # TODO: possibly allow full volume mounting spec
    reports_volume = k8s_client.V1Volume(
        name=reports_pvc,
        persistent_volume_claim=k8s_client.V1PersistentVolumeClaimVolumeSource(
            claim_name=reports_pvc
        ),
    )

    reports_volume_mount = k8s_client.V1VolumeMount(
        name=reports_pvc, mount_path=os.path.join("/", reports_mount_path)
    )

    pod_env = [
        k8s_client.V1EnvVar(name="TASK_TYPE", value="kube"),
        k8s_client.V1EnvVar(name="POD_NAMESPACE", value=namespace),
        k8s_client.V1EnvVar(name="RUN_ID", value=test_engine_name),
    ]

    if tests_mount_path is not None:
        pod_env.append(k8s_client.V1EnvVar(name="TESTS_FOLDER", value=tests_mount_path))

    if reports_mount_path is not None:
        pod_env.append(
            k8s_client.V1EnvVar(name="REPORTS_FOLDER", value=reports_mount_path)
        )

    # Allows user to overwrite with own env vars
    if engine_config is not None:
        pod_env.extend(
            [
                k8s_client.V1EnvVar(name=key, value=value)
                for key, value in engine_config.items()
            ]
        )

    if engine_service_account is None:
        engine_service_account = "cicada-engine-account"

    pod_body = k8s_client.V1Pod(
        metadata=k8s_client.V1ObjectMeta(
            name=test_engine_name,
            labels={
                "run_id": test_engine_name,
                "run": test_engine_name,
                "family": "cicada",
                "type": "cicada-engine",
            },
        ),
        spec=k8s_client.V1PodSpec(
            restart_policy="Never",
            containers=[
                k8s_client.V1Container(
                    image="cicadatesting/cicada-2-engine:latest",
                    name=test_engine_name,
                    volume_mounts=[tests_volume_mount, reports_volume_mount],
                    env=pod_env,
                )
            ],
            volumes=[tests_volume, reports_volume],
            service_account_name=engine_service_account,
        ),
    )

    return run_pod_to_completion(namespace, pod_body)
