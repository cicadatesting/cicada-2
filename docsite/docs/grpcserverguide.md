---
id: grpc-server-guide
title: gRPC Server Guide
sidebar_label: gRPC Server Guide
---

In this guide, you'll create a gRPC service and test it using the gRPC runner.

[Source code](https://github.com/herzo175/cicada-2/tree/master/example_services/grpc_server)

## App

First, we'll need to create our gRPC server. We can use the 'hello world'
example from the gRPC website:

`protos/app.proto`

```proto
syntax = "proto3";

package app;

service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply) {}
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
```

`app.py`

```python
from concurrent import futures
import logging

import grpc

import app_pb2
import app_pb2_grpc


class Greeter(app_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        return app_pb2.HelloReply(message='Hello, %s!' % request.name)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    app_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
```

`Makefile`

```Makefile
.PHONY=proto-compile

proto-compile:
	python3 -m grpc_tools.protoc -I ./protos \
		--python_out=. \
		--grpc_python_out=. \
		./protos/app.proto
```

Run `make proto-compile` to generate the stubs

## Environment

We can use docker-compose to launch our app. To do this, we'll need to create
a Dockerfile and a compose file.

`Dockerfile`

```Dockerfile
FROM python:3.8-slim-buster

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app.py .
ADD app_pb2.py .
ADD app_pb2_grpc.py .

EXPOSE 50051

ENTRYPOINT ["python", "-u", "/app/app.py"]
```

`docker-compose.yml`

```
version: '3'
services:
  service:
    build: .
    ports:
      - 50051:50051
```

`Makefile`

```Makefile
.PHONY=services,run,clean,proto-compile
WORKDIR=$(shell pwd)

export WORKDIR

...

services:
	docker-compose up service

run:
	docker-compose up --build --abort-on-container-exit --remove-orphans

clean:
	docker-compose down --remove-orphans
```

Run `make run` and ensure the service starts properly

## Tests

Finally, we'll create a test that uses Cicada to invoke the gRPC runner against
our service. This test will expect the response message to be "Hello, jeff!".

Also, make sure to mount the proto files to the `incoming_protos` folder inside
the runner

`test.cicada.yaml`

```yaml
description: Example gRPC test
tests:
  - name: greeter-requests
    description: Send requests to greeter service
    runner: grpc-runner
    template: >
      volumes:
        - source: {{ getenv("WORKDIR") }}/protos
          destination: /incoming_protos
    asserts:
      - type: ResponseAssert
        params:
          actionType: Unary
          expected:
            message: "Hello, jeff!"
          actionParams:
            proto: app
            service: Greeter
            serviceAddress: service:50051
            method: SayHello
            requestType: HelloRequest
            message:
              name: jeff
```

`docker-compose.yml`

```yaml
...
services:
  ...
  cicada:
    image: cicadatesting/cicada-2-engine
    environment:
      - CONTAINER_NETWORK=grpc_server_default
      - WORKDIR=${WORKDIR}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - .:/tests
      - ./reports:/reports
    depends_on:
      - service
```

Run `make run` again to start the service and Cicada. Ensure that it runs
the tests successfully and generates the report files.

Congratulations on creating and testing an gRPC service!
