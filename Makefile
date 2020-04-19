.PHONY=build-engine,build-env,build-runner,run-env,proto-compile

DOCKER_PROVIDER=jeremyaherzog

build-engine:
	docker build -f dockerfiles/engine.dockerfile -t ${DOCKER_PROVIDER}/cicada-2-engine .

build-env:
	docker build -f dockerfiles/env.dockerfile -t ${DOCKER_PROVIDER}/cicada-2-env .

build-runner:
	docker build -f dockerfiles/${RUNNER_NAME}.dockerfile -t ${DOCKER_PROVIDER}/cicada-2-${RUNNER_NAME} .

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
