import json

import grpc
from grpc_status import rpc_status
from google.protobuf.empty_pb2 import Empty

from cicada2.protos import runner_pb2, runner_pb2_grpc
from cicada2.engine.types import ActionResult, AssertResult


def send_action(runner_address: str, action: dict) -> ActionResult:
    with grpc.insecure_channel(runner_address) as channel:
        stub = runner_pb2_grpc.RunnerStub(channel)
        request = runner_pb2.ActionRequest(
            type=action['type'],
            params=json.dumps(action['params']).encode('utf-8')
        )

        try:
            response: runner_pb2.ActionReply = stub.Action(request)
            return json.loads(response.outputs)
        except grpc.RpcError as err:
            # status = rpc_status.from_call(err)
            # TODO: log error
            print(err)

            return {}


def send_assert(runner_address: str, asrt: dict) -> AssertResult:
    with grpc.insecure_channel(runner_address) as channel:
        stub = runner_pb2_grpc.RunnerStub(channel)
        request = runner_pb2.AssertRequest(
            type=asrt['type'],
            params=json.dumps(asrt['params']).encode('utf-8')
        )

        try:
            response: runner_pb2.AssertReply = stub.Assert(request)

            return AssertResult(
                passed=response.passed,
                actual=response.actual,
                expected=response.expected,
                description=response.description
            )
        except grpc.RpcError as err:
            status = rpc_status.from_call(err)
            # TODO: log error

            return AssertResult(
                passed=False,
                actual=None,
                expected=None,
                description=status.details
            )


def runner_healthcheck(runner_address: str) -> bool:
    # NOTE: possibly use built in grpc health check
    with grpc.insecure_channel(runner_address) as channel:
        stub = runner_pb2_grpc.RunnerStub(channel)

        try:
            response = stub.Healthcheck(Empty())
            return response.ready
        except grpc.RpcError as err:
            print(err)
            return False
