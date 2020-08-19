.PHONY=build-engine,build-env,build-runner,run-env,proto-compile

build-engine:
	docker build -f dockerfiles/engine.dockerfile -t jeremyaherzog/cicada-2-engine:local .
ifdef K3D
	k3d image import jeremyaherzog/cicada-2-engine:local
endif

build-env:
	docker build -f dockerfiles/env.dockerfile -t jeremyaherzog/cicada-2-env .

build-runner:
	docker build -f dockerfiles/${RUNNER_NAME}.dockerfile -t jeremyaherzog/cicada-2-${RUNNER_NAME} .
ifdef K3D
	k3d image import jeremyaherzog/cicada-2-${RUNNER_NAME}:latest
endif

run-env:
	docker run -it --rm \
		--name cicada-2-env \
		--network cicada-2 \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(shell pwd):/opt \
		jeremyaherzog/cicada-2-env \
		/bin/bash

lint:
	python3 -m pylint cicada2

test:
	python3 -m pytest cicada2

clean:
	docker container stop $(shell docker ps -q --filter "label=cicada-2-runner")

proto-compile:
	python3 -m grpc_tools.protoc -I . \
		--python_out=. \
		--grpc_python_out=. \
		cicada2/protos/*.proto
