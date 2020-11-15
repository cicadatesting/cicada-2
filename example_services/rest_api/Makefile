.PHONY=build,services,run,clean
ENGINE_IMAGE=cicadatesting/cicada-2-engine
REST_RUNNER_IMAGE=cicadatesting/cicada-2-rest-runner
SQL_RUNNER_IMAGE=cicadatesting/cicada-2-sql-runner

export ENGINE_IMAGE
export REST_RUNNER_IMAGE
export SQL_RUNNER_IMAGE

build:
	docker build . -t cicadatesting/rest-api-example:local
ifdef K3D
	k3d image import cicadatesting/rest-api-example:local
endif

k3d-setup:
	kubectl apply -f pvc.yaml
	sleep 5
	kubectl cp test.cicada.yaml initializer:/tests
	kubectl cp V1__Initial.sql initializer:/flyway

services:
	docker-compose -f compose-services.yml up -d --build

run:
ifdef K3D
	kubectl apply -f workflow.yaml
else
	docker-compose -f compose-test.yml up --exit-code-from cicada
endif

get-reports:
	kubectl cp initializer:/reports reports

clean:
ifdef K3D
	kubectl delete -f workflow.yaml
	kubectl delete -f pvc.yaml
else
	docker-compose -f compose-services.yml down --remove-orphans
endif
