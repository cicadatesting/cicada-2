import json
from typing import Any, Dict

import grpc
from google.protobuf.empty_pb2 import Empty

from cicada2.protos import runner_pb2, runner_pb2_grpc


def send_action(runner_address: str, action: dict) -> dict:
    with grpc.insecure_channel(runner_address) as channel:
        stub = runner_pb2_grpc.RunnerStub(channel)
        request = runner_pb2.ActionRequest(
            type=action['type'],
            params=json.dumps(action['params']).encode('utf-8')
        )

        response = stub.Action(request)
        # TODO: track error/error handling
        return json.loads(response.outputs)


def send_assert(runner_address: str, asrt: dict) -> bool:
    with grpc.insecure_channel(runner_address) as channel:
        stub = runner_pb2_grpc.RunnerStub(channel)
        request = runner_pb2.AssertRequest(
            type=asrt['type'],
            params=json.dumps(asrt['params']).encode('utf-8')
        )

        response = stub.Assert(request)
        # TODO: track error/error handling
        return response.passed


def runner_healthcheck(runner_address: str) -> bool:
    with grpc.insecure_channel(runner_address) as channel:
        stub = runner_pb2_grpc.RunnerStub(channel)

        try:
            response = stub.Healthcheck(Empty())
        except grpc.RpcError as err:
            print(err)
            return False

        return response.ready
