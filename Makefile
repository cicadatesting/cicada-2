.PHONY=build-env,run-env

build-env:
	docker build -f dockerfiles/env.dockerfile -t cicada-2-env .

build-runner:
	docker build -f dockerfiles/${RUNNER_NAME}.dockerfile -t ${RUNNER_NAME} .

start-runner:
	docker run --rm \
		--name ${RUNNER_NAME} \
		-p 50051:50051 \
		${RUNNER_NAME}

run-env:
	docker run -it --rm \
		--name cicada-2-env \
		--network cicada-2 \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(shell pwd):/opt \
		cicada-2-env \
		/bin/bash

proto-compile:
	python3 -m grpc_tools.protoc -I . \
		--python_out=. \
		--grpc_python_out=. \
		cicada2/protos/*.proto
