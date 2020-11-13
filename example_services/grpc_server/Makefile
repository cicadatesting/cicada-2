.PHONY=services,run,clean,proto-compile
WORKDIR=$(shell pwd)

export WORKDIR

services:
	docker-compose up -d --build service

run:
	docker-compose up --build --exit-code-from cicada --remove-orphans

clean:
	docker-compose down --remove-orphans

proto-compile:
	python3 -m grpc_tools.protoc -I ./protos \
		--python_out=. \
		--grpc_python_out=. \
		./protos/app.proto