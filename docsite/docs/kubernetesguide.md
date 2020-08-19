---
id: kubernetes-guide
title: Kubernetes Guide
sidebar_label: Kubernetes Guide
---

In this guide, you'll set up the rest runner example to run on kubernetes.

## Setup

As a prerequisite, the Cicada engine will need privileges to create, list, and
delete services in the namespace it will be operating in. The yaml below can be
used to create a service account with the necessary roles:

<!--TODO: downloadable links to yaml-->

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: default
  name: cicada-engine-role
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["create", "delete", "deletecollection", "list"]
---
apiVersion: v1
kind: ServiceAccount
metadata:
  creationTimestamp: null
  name: cicada-engine-account
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cicada-engine-pod
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cicada-engine-role
subjects:
- kind: ServiceAccount
  name: cicada-engine-account
  namespace: default
```

## Environment

In order to pass test files and reports between our local environment and the
cluster, we will use kubernetes volumes. To begin, create
`PersistentVolumeClaims` for the database migration files, test files, and
report files:

<!--TODO: downloadable links to yaml-->

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

After creating the PVC's, we will start a pod that can bind to them for the
purpose of uploading the files, called `initializer`:

```yaml
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

## Running

To run Cicada, create a pod for the engine that binds to the tests and reports
volumes:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cicada
  labels:
    run: cicada
spec:
  serviceAccountName: cicada-engine-account
  restartPolicy: Never
  containers:
    - image: jeremyaherzog/cicada-2-engine
      name: cicada
      env:
        - name: TASK_TYPE
          value: kube
      volumeMounts:
        - mountPath: /tests
          name: tests-volume
        - mountPath: /reports
          name: reports-volume
  volumes:
    - name: tests-volume
      persistentVolumeClaim:
        claimName: tests-pvc
    - name: reports-volume
      persistentVolumeClaim:
        claimName: reports-pvc
```

Make sure that the environment variable `TASK_TYPE` is set to `kube` and that
it is using the `cicada-engine-account` service account or a service account
with the correct permissions.

Once the pod completes, the reports will be ready!

## Collecting reports

To collect the reports, simply copy them from the `initializer` pod to a local
directory:

```bash
kubectl cp initializer:/reports reports
```
