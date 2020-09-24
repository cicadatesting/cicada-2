import os

import kopf
from kubernetes import client as k8s_client
from kubernetes.client.rest import ApiException

from cicada2.operator.daemon import pods
from cicada2.operator.daemon.types import TestEngineBody


@kopf.on.create("cicada.io", "v1", "testengines")
def create_fn(body: TestEngineBody):
    # pylint: disable=too-many-statements
    # check if dependent pods have finished running
    # create io_utility pod, wait until status is completed
    # launch engine, wait until status is completed
    # create io_utility pod to run post completion file transfers
    # clean up pods with shared test label (on CRD delete)
    name = body["metadata"]["name"]
    namespace = body["metadata"]["namespace"]
    spec = body["spec"]

    try:
        assert "tests" in spec, "spec missing 'tests' section"
        assert "reports" in spec, "spec missing 'tests' section"

        assert "pvc" in spec["tests"], "'tests' section must have 'pvc'"
        assert "pvc" in spec["reports"], "'reports' section must have 'pvc'"
    except AssertionError as err:
        raise kopf.PermanentError(f"Invalid spec: {err}")

    if "dependencies" in spec:
        try:
            for dependency in spec["dependencies"]:
                pod_name = dependency.get("name")
                pod_labels = dependency.get("labels")
                pod_statuses = dependency.get("statuses")

                pods.check_dependent_pods(
                    namespace=namespace,
                    name=pod_name,
                    statuses=pod_statuses,
                    labels=pod_labels,
                )
        except (ApiException, RuntimeError) as err:
            raise kopf.TemporaryError(
                f"Encountered problem checking dependent pods: {err}"
            )
        except AssertionError as err:
            raise kopf.PermanentError(f"Must resolve issue with dependencies: {err}")

    created_pods = {}

    if "remotePath" in spec["tests"]:
        try:
            tests = spec["tests"]

            pvc_name = tests["pvc"]

            local_path = tests.get("localPath", os.path.join("/", pvc_name))
            remote_path = tests["remotePath"]

            transfer_path = f"{remote_path}==file://{local_path}"

            pre_transfer_pod = pods.run_io_utility(
                test_engine_name=name,
                namespace=namespace,
                pvc_name=pvc_name,
                io_config=spec.get("ioConfig", {}),
                transfer_path=transfer_path,
            )

            kopf.info(
                body,
                reason="StepComplete",
                message=f"Completed running post transfer pod (name: {pre_transfer_pod.metadata.name})",
            )
            created_pods["pre_transfer"] = pre_transfer_pod
        except ApiException as err:
            raise kopf.TemporaryError(f"Encountered problem with io utility: {err}")
        except (AssertionError, RuntimeError) as err:
            raise kopf.PermanentError(f"Must resolve issue with io utility: {err}")

    try:
        engine_pod = pods.run_engine(
            test_engine_name=name,
            namespace=namespace,
            tests_pvc=spec["tests"]["pvc"],
            reports_pvc=spec["reports"]["pvc"],
            tests_mount_path=spec["tests"].get("mountPath", "/tests"),
            reports_mount_path=spec["reports"].get("mountPath", "/reports"),
            engine_service_account=spec.get("engineServiceAccount"),
            engine_config=spec.get("engineConfig"),
        )

        kopf.info(
            body,
            reason="StepComplete",
            message=f"Completed running post transfer pod (name: {engine_pod.metadata.name})",
        )
        created_pods["engine"] = engine_pod
    except ApiException as err:
        raise kopf.TemporaryError(f"Encountered problem with engine: {err}")
    except RuntimeError as err:
        raise kopf.PermanentError(f"Must resolve issue with engine: {err}")

    if "remotePath" in spec["reports"]:
        try:
            reports = spec["reports"]

            pvc_name = reports["pvc"]

            local_path = reports.get("localPath", os.path.join("/", pvc_name))
            remote_path = reports["remotePath"]

            transfer_path = f"file://{local_path}=={remote_path}"

            post_transfer_pod = pods.run_io_utility(
                test_engine_name=name,
                namespace=namespace,
                pvc_name=pvc_name,
                io_config=spec.get("ioConfig", {}),
                transfer_path=transfer_path,
            )

            kopf.info(
                body,
                reason="StepComplete",
                message=f"Completed running post transfer pod (name: {post_transfer_pod.metadata.name})",
            )
            created_pods["post_transfer"] = post_transfer_pod
        except ApiException as err:
            raise kopf.TemporaryError(f"Encountered problem with io utility: {err}")
        except (AssertionError, RuntimeError) as err:
            raise kopf.PermanentError(f"Must resolve issue with io utility: {err}")

    return created_pods


@kopf.on.delete("cicada.io", "v1", "testengines")
def delete_fn(body: dict):
    api = k8s_client.CoreV1Api()

    name: str = body["metadata"]["name"]
    namespace: str = body["metadata"]["namespace"]

    try:
        api.delete_collection_namespaced_pod(
            namespace=namespace, label_selector=f"run_id={name}"
        )

        # Clean up straggler services
        service_list = api.list_namespaced_service(
            namespace=namespace, label_selector=f"run_id={name}"
        ).items

        for service in service_list:
            api.delete_namespaced_service(
                name=service.metadata.name, namespace=namespace
            )
    except ApiException as err:
        raise kopf.TemporaryError(f"Failed to delete engine pods: {err}")
