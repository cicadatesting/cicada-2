.PHONY=build-engine,build-env,build-runner,run-env,proto-compile

build-engine:
	docker build -f dockerfiles/engine.dockerfile -t cicadatesting/cicada-2-engine:latest .
ifdef K3D
	k3d image import cicadatesting/cicada-2-engine:latest
endif

build-env:
	docker build -f dockerfiles/env.dockerfile -t cicadatesting/cicada-env .

build-runner:
	docker build -f dockerfiles/${RUNNER_NAME}.dockerfile -t cicadatesting/cicada-2-${RUNNER_NAME} .
ifdef K3D
	k3d image import cicadatesting/cicada-2-${RUNNER_NAME}:latest
endif

build-io-utility:
	docker build -f dockerfiles/operator.io-utility.dockerfile -t cicadatesting/cicada-operator-io-utility .
ifdef K3D
	k3d image import cicadatesting/cicada-operator-io-utility:latest
endif

build-operator:
	docker build -f dockerfiles/operator.daemon.dockerfile -t cicadatesting/cicada-operator:latest .
ifdef K3D
	k3d image import cicadatesting/cicada-operator:latest
endif

build-verification:
	docker build -f dockerfiles/verification.dockerfile -t cicadatesting/cicada-verification:latest .
ifdef K3D
	k3d image import cicadatesting/cicada-verification:latest
endif

run-env:
	docker run -it --rm \
		--name cicada-env \
		--network cicada \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(shell pwd):/opt \
		cicadatesting/cicada-env \
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
