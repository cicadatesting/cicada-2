from unittest.mock import patch, MagicMock
import pytest

from cicada2.operator.daemon import pods


@patch("cicada2.operator.daemon.pods.k8s_client")
def test_check_dependent_pods_labels(k8s_client_mock):
    core_v1_api_mock = MagicMock()
    return_pods_mock = MagicMock()
    pod_a = MagicMock()
    pod_b = MagicMock()

    pod_a.status.phase = "Running"
    pod_b.status.phase = "Succeeded"

    return_pods_mock.items = [pod_a, pod_b]
    core_v1_api_mock.list_namespaced_pod.return_value = return_pods_mock

    k8s_client_mock.CoreV1Api.return_value = core_v1_api_mock

    pods.check_dependent_pods(namespace="some-namespace", labels={"foo": "bar"})


@patch("cicada2.operator.daemon.pods.k8s_client")
def test_check_dependent_pods_name(k8s_client_mock):
    core_v1_api_mock = MagicMock()
    pod = MagicMock()

    pod.status.phase = "Running"

    core_v1_api_mock.read_namespaced_pod.return_value = pod

    k8s_client_mock.CoreV1Api.return_value = core_v1_api_mock

    pods.check_dependent_pods(namespace="some-namespace", name="some-name")


@patch("cicada2.operator.daemon.pods.k8s_client")
def test_check_dependent_throws_exception(k8s_client_mock):
    core_v1_api_mock = MagicMock()
    pod = MagicMock()

    pod.status.phase = "Failed"

    core_v1_api_mock.read_namespaced_pod.return_value = pod

    k8s_client_mock.CoreV1Api.return_value = core_v1_api_mock

    with pytest.raises(RuntimeError):
        pods.check_dependent_pods(namespace="some-namespace", name="some-name")


@patch("cicada2.operator.daemon.pods.run_pod_to_completion")
def test_run_io_utility(run_pod_to_completion_mock):
    pods.run_io_utility(
        "some-engine-name",
        "some-namespace",
        "tests-pvc",
        io_config={},
        transfer_path="some-transfer-path",
    )

    run_pod_to_completion_mock.assert_called_once()

    pod_body = run_pod_to_completion_mock.call_args.args[1]

    assert pod_body.metadata.labels["family"] == "cicada"
    assert pod_body.metadata.labels["type"] == "cicada-io-utility"
    assert pod_body.metadata.labels["run_id"] == "some-engine-name"

    assert pod_body.spec.containers[0].args == ["transfer", "some-transfer-path"]
    assert pod_body.spec.containers[0].volume_mounts[0].name == "tests-pvc"
    assert pod_body.spec.containers[0].volume_mounts[0].mount_path == "/tests-pvc"

    assert pod_body.spec.volumes[0].name == "tests-pvc"
    assert pod_body.spec.volumes[0].persistent_volume_claim.claim_name == "tests-pvc"


@patch("cicada2.operator.daemon.pods.run_pod_to_completion")
def test_run_engine(run_pod_to_completion_mock):
    pods.run_engine(
        test_engine_name="some-engine-name",
        namespace="some-namespace",
        tests_pvc="tests-pvc",
        reports_pvc="reports-pvc",
        tests_mount_path="/tests",
        reports_mount_path="/reports",
    )

    run_pod_to_completion_mock.assert_called_once()

    pod_body = run_pod_to_completion_mock.call_args.args[1]

    assert pod_body.metadata.labels["family"] == "cicada"
    assert pod_body.metadata.labels["type"] == "cicada-engine"
    assert pod_body.metadata.labels["run_id"] == "some-engine-name"

    assert pod_body.spec.containers[0].volume_mounts[0].name == "tests-pvc"
    assert pod_body.spec.containers[0].volume_mounts[0].mount_path == "/tests"

    assert pod_body.spec.containers[0].volume_mounts[1].name == "reports-pvc"
    assert pod_body.spec.containers[0].volume_mounts[1].mount_path == "/reports"

    assert pod_body.spec.containers[0].env[0].name == "TASK_TYPE"
    assert pod_body.spec.containers[0].env[0].value == "kube"
    assert pod_body.spec.containers[0].env[1].name == "POD_NAMESPACE"
    assert pod_body.spec.containers[0].env[1].value == "some-namespace"
    assert pod_body.spec.containers[0].env[2].name == "RUN_ID"
    assert pod_body.spec.containers[0].env[2].value == "some-engine-name"
    assert pod_body.spec.containers[0].env[3].name == "TESTS_FOLDER"
    assert pod_body.spec.containers[0].env[3].value == "/tests"
    assert pod_body.spec.containers[0].env[4].name == "REPORTS_FOLDER"
    assert pod_body.spec.containers[0].env[4].value == "/reports"

    assert pod_body.spec.volumes[0].name == "tests-pvc"
    assert pod_body.spec.volumes[0].persistent_volume_claim.claim_name == "tests-pvc"

    assert pod_body.spec.volumes[1].name == "reports-pvc"
    assert pod_body.spec.volumes[1].persistent_volume_claim.claim_name == "reports-pvc"
