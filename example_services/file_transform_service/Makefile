.PHONY=services,run,clean

WORKDIR=$(shell pwd)
ENGINE_IMAGE=cicadatesting/cicada-2-engine
KAFKA_RUNNER_IMAGE=cicadatesting/cicada-2-kafka-runner
S3_RUNNER_IMAGE=cicadatesting/cicada-2-s3-runner

export WORKDIR
export ENGINE_IMAGE
export KAFKA_RUNNER_IMAGE
export S3_RUNNER_IMAGE

services:
	docker-compose up -d --build service

run:
	docker-compose up --build --exit-code-from cicada --remove-orphans

clean:
	docker-compose down
