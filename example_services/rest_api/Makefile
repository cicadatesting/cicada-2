.PHONY=build,services,run,clean

build:
	docker build . -t jeremyaherzog/rest-api-example:local
ifdef K3D
	k3d image import jeremyaherzog/rest-api-example:local
endif

k3d-setup:
	kubectl apply -f pvc.yaml
	kubectl apply -f initializer.yaml
	sleep 5
	kubectl cp test.cicada.yaml initializer:/tests
	kubectl cp V1__Initial.sql initializer:/flyway

services:
ifdef K3D
	kubectl apply -f services.yaml
else
	docker-compose up api
endif

run:
ifdef K3D
	kubectl apply -f engine.yaml
else
	docker-compose up --build --remove-orphans
endif

get-reports:
	kubectl cp initializer:/reports reports

clean:
ifdef K3D
	kubectl delete -f engine.yaml
	kubectl delete -f services.yaml
	kubectl delete -f initializer.yaml
	kubectl delete -f pvc.yaml
else
	docker-compose down -remove-orphans
endif
