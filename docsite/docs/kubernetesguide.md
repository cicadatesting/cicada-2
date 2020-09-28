---
id: kubernetes-guide
title: Kubernetes Guide
sidebar_label: Kubernetes Guide
---

In this guide, you'll set up the rest runner example to run on kubernetes.

## Setup

As a prerequisite, the Cicada operator will need to be installed. The operator
can be used to start the engine as well as download and upload requisite tests
and reports from Git or an S3 compatiable filestore.

Helm:

```bash
# Add Helm repo
helm repo add cicada-charts https://cicadatesting.github.io/cicada-charts
helm repo update
# Make sure cicada-charts/cicada-operator-chart is displayed
helm search repo cicada-charts
# Install Helm chart
helm install cicada-operator cicada-charts/cicada-operator-chart
```

YAML:

```bash
# Install the operator CRD's
kubectl apply -f https://cicadatesting.github.io/cicada-charts/operator/templates/crd.yaml
# Install roles for operator, engine, runners
kubectl apply -f https://cicadatesting.github.io/cicada-charts/operator/templates/rbac.yaml
# Start Cicada operator
kubectl apply -f https://cicadatesting.github.io/cicada-charts/operator/templates/deployment.yaml
```

## Environment

In order to pass test files and reports between our local environment and the
cluster, we will use kubernetes volumes. To begin, create
`PersistentVolumeClaims` for the database migration files, test files, and
report files:

`pvc.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: flyway-pvc
spec:
  storageClassName: local-path
  resources:
    requests:
      storage: 128Mi
  accessModes:
    - ReadWriteOnce
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: tests-pvc
spec:
  storageClassName: local-path
  resources:
    requests:
      storage: 128Mi
  accessModes:
    - ReadWriteOnce
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: reports-pvc
spec:
  storageClassName: local-path
  resources:
    requests:
      storage: 128Mi
  accessModes:
    - ReadWriteOnce
```

NOTE: These PVC's use a storage class called `local-path`. Be sure to use a
storage class appropriate for your cluster.

After creating the PVC's, we will start a pod that can bind to them for the
purpose of uploading the files, called `initializer`.

`pvc.yaml`

```yaml
...
---
apiVersion: v1
kind: Pod
metadata:
  name: initializer
spec:
  containers:
  - image: busybox
    name: initializer
    command: ["ping", "127.0.0.1"]
    volumeMounts:
      - mountPath: "/flyway"
        name: flyway-volume
      - mountPath: "/tests"
        name: tests-volume
      - mountPath: "/reports"
        name: reports-volume
  volumes:
    - name: flyway-volume
      persistentVolumeClaim:
        claimName: flyway-pvc
    - name: tests-volume
      persistentVolumeClaim:
        claimName: tests-pvc
    - name: reports-volume
      persistentVolumeClaim:
        claimName: reports-pvc
```

After starting the pod, run the following commands to upload test files to
the correct volumes:

```bash
kubectl cp test.cicada.yaml initializer:/tests
kubectl cp V1__Initial.sql initializer:/flyway
```

If you are using a utility like `ksync`, you can bind the
current directory to the `/flyway`, `/tests`, and `/reports`
directories to skip the manual copies.

## Services

To run the application in kubernetes, create a file called `workflow.yaml` to specify the pods and services:

`workflow.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: db
  labels:
    run: db
spec:
  containers:
    - image: postgres:12-alpine
      name: db
      env:
        - name: POSTGRES_PASSWORD
          value: admin
      ports:
        - containerPort: 5432
---
apiVersion: v1
kind: Service
metadata:
  name: db
spec:
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    run: db
---
apiVersion: v1
kind: Pod
metadata:
  name: flyway
  labels:
    run: flyway
spec:
  restartPolicy: Never
  containers:
    - image: flyway/flyway:6-alpine
      name: flyway
      args:
      - -url=jdbc:postgresql://db:5432/
      - -schemas=public
      - -user=postgres
      - -password=admin
      - -connectRetries=60
      - migrate
      volumeMounts:
        - mountPath: /flyway/sql
          name: flyway-volume
  volumes:
    - name: flyway-volume
      persistentVolumeClaim:
        claimName: flyway-pvc
---
apiVersion: v1
kind: Pod
metadata:
  name: api
  labels:
    run: api
spec:
  restartPolicy: Never
  containers:
    - image: cicadatesting/rest-api-example:latest
      name: api
      ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  ports:
    - port: 8080
      targetPort: 8080
  selector:
    run: api
```

This will start the database and API, as well as apply migrations to
the database.

## Running

To run Cicada, create a pod for the engine that binds to the tests and reports
volumes:

`workflow.yaml`

```yaml
apiVersion:  cicada.io/v1
kind: TestEngine
metadata:
  name: rest-api-test
spec:
  dependencies:
    - name: api
      statuses:
        - Running
  tests:
    pvc: tests-pvc
  reports:
    pvc: reports-pvc
```

Run the service using `kubectl apply -f workflow.yaml`. Once the engine pods complete, the reports will be ready!

## Collecting reports

To collect the reports, simply copy them from the `initializer` pod to a local
directory:

```bash
kubectl cp initializer:/reports reports
```
