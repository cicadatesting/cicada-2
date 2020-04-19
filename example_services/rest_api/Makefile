.PHONY=build,run,clean

build:
	docker build -t example-rest-api .

services:
	docker-compose up api

run:
	docker-compose up

clean:
	docker-compose down
