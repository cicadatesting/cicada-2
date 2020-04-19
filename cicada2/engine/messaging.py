import json
from typing import Optional

import grpc
from google.protobuf.empty_pb2 import Empty

from cicada2.shared.logs import get_logger
from cicada2.protos import runner_pb2, runner_pb2_grpc
from cicada2.shared.types import ActionResult, AssertResult


LOGGER = get_logger("messaging")

# NOTE: stream action requests and results for multiple executions?
# NOTE: support for non-json types with encoding param?


def send_action(runner_address: str, action: dict) -> Optional[ActionResult]:
    with grpc.insecure_channel(runner_address) as channel:
        stub = runner_pb2_grpc.RunnerStub(channel)
        request = runner_pb2.ActionRequest(
            type=action["type"], params=json.dumps(action["params"]).encode("utf-8")
        )

        try:
            response: runner_pb2.ActionReply = stub.Action(request)
            return json.loads(response.outputs)
        except json.JSONDecodeError as err:
            LOGGER.warning("Runner did not return JSON encoded action response")
        except grpc.RpcError as err:
            LOGGER.warning("Received %s during send_action: %s", err.code(), err)

        # TODO: unit test for None return
        return None


def send_assert(runner_address: str, asrt: dict) -> AssertResult:
    with grpc.insecure_channel(runner_address) as channel:
        stub = runner_pb2_grpc.RunnerStub(channel)
        request = runner_pb2.AssertRequest(
            type=asrt["type"], params=json.dumps(asrt["params"]).encode("utf-8")
        )

        try:
            response: runner_pb2.AssertReply = stub.Assert(request)

            return AssertResult(
                passed=response.passed,
                actual=response.actual,
                expected=response.expected,
                description=response.description,
            )
        except grpc.RpcError as err:
            LOGGER.warning("Received %s during send_assert: %s", err.code(), err)

            return AssertResult(
                passed=False, actual=None, expected=None, description=err.details()
            )


def runner_healthcheck(runner_address: str) -> bool:
    # NOTE: possibly use built in grpc health check
    with grpc.insecure_channel(runner_address) as channel:
        stub = runner_pb2_grpc.RunnerStub(channel)

        try:
            response = stub.Healthcheck(Empty())
            return response.ready
        except grpc.RpcError as err:
            LOGGER.warning("Received %s during healthcheck: %s", err.code(), err)
            return False
