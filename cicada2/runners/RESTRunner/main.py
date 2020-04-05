import time
from threading import Thread
from concurrent import futures
import json

import grpc

from cicada2.protos import runner_pb2, runner_pb2_grpc
from cicada2.runners.RESTRunner import runner


class RESTRunnerServer(runner_pb2_grpc.RunnerServicer):
    def Action(self, request, context):
        outputs = runner.run_action(
            action_type=request.type,
            params=json.loads(request.params)
        )

        return runner_pb2.ActionReply(
            outputs=json.dumps(outputs).encode('utf-8')
        )

    def Assert(self, request, context):
        return runner.runner_pb2.AssertReply(passed=True)

    def Healthcheck(self, request, context):
        return runner_pb2.HealthcheckReply(ready=True)


def main():
    server = grpc.server(futures.ThreadPoolExecutor())

    runner_pb2_grpc.add_RunnerServicer_to_server(RESTRunnerServer(), server)

    server.add_insecure_port('[::]:50051')
    server.start()
    # server.wait_for_termination()
    
    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()
