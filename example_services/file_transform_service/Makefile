.PHONY=services,run,clean

WORKDIR=$(shell pwd)

export WORKDIR

services:
	docker-compose up -d --build service

run:
	docker-compose up --build --exit-code-from cicada --remove-orphans

clean:
	docker-compose down
