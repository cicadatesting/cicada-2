import time
from concurrent import futures
import json

import grpc

from cicada2.protos import runner_pb2, runner_pb2_grpc
from cicada2.runners.sql_runner import runner


# TODO: need a nicer way to test runners individually
class SQLRunnerServer(runner_pb2_grpc.RunnerServicer):
    def Action(self, request, context):
        try:
            outputs = runner.run_action(
                action_type=request.type, params=json.loads(request.params)
            )

            return runner_pb2.ActionReply(outputs=json.dumps(outputs))
        except ValueError as e:
            # NOTE: use abort_with_status?
            context.abort(code=grpc.StatusCode.INVALID_ARGUMENT, details=e)
        except RuntimeError as e:
            context.abort(code=grpc.StatusCode.UNAVAILABLE, details=e)

    def Assert(self, request, context):
        try:
            result = runner.run_assert(
                assert_type=request.type, params=json.loads(request.params)
            )

            return runner_pb2.AssertReply(
                passed=result["passed"],
                expected=result.get("expected"),
                actual=result.get("actual"),
                description=result.get("description"),
            )
        except ValueError as e:
            context.abort(code=grpc.StatusCode.INVALID_ARGUMENT, details=str(e))
        except RuntimeError as e:
            context.abort(code=grpc.StatusCode.UNAVAILABLE, details=str(e))

    def Healthcheck(self, request, context):
        return runner_pb2.HealthcheckReply(ready=True)


def main():
    server = grpc.server(futures.ThreadPoolExecutor())

    runner_pb2_grpc.add_RunnerServicer_to_server(SQLRunnerServer(), server)

    server.add_insecure_port("[::]:50051")
    server.start()
    # server.wait_for_termination()

    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
