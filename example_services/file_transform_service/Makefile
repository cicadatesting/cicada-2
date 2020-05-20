.PHONY=services,run,clean

WORKDIR=$(shell pwd)

export WORKDIR

services:
	docker-compose up service

run:
	docker-compose up --build

clean:
	docker-compose down
