---
id: test-engine
title: Test Engine
sidebar_label: Test Engine
---

The TestEngine is a Kubernetes resource for creating the Cicada engine and
managing file transfer before and after running Cicada

<pre><code>
apiVersion:  cicada.io/v1
kind: TestEngine
metadata:
  name: your-test-name
spec:
  dependencies:
    - name: <a href="#dependenciesname">string</a>
      labels: <a href="#dependencieslabels">Map[string, string]</a>
      statuses: <a href="#dependenciesstatuses">List[string]</a>
  ioConfig:
    S3_ENDPOINT: <a href="#ioconfigs3_endpoint">string</a>
    S3_REGION: <a href="#ioconfigs3_region">string</a>
    S3_ACCESS_KEY_ID: <a href="#ioconfigs3_access_key_id">string</a>
    S3_SECRET_ACCESS_KEY: <a href="#ioconfigs3_secret_access_key">string</a>
  engineConfig: <a href="#engineconfig">Map[string, string]</a>
  tests:
    pvc: <a href="#testspvc">string</a>
    mountPath: <a href="#testsmountpath">string</a>
    remotePath: <a href="#testsremotepath">string</a>
    localPath: <a href="#testslocalpath">string</a>
  reports:
    pvc: <a href="#reportspvc">string</a>
    mountPath: <a href="#reportsmountpath">string</a>
    remotePath: <a href="#reportsremotepath">string</a>
    localPath: <a href="#reportslocalpath">string</a>
</code></pre>

## dependencies

### dependencies.name

Name of pod to check statuses of (optional)

### dependencies.labels

Labels to find pods with if name is not specified

### dependencies.statuses

List of allowed statuses for found pods to be in for check to succeed. Defaults
to "Running" and "Succeeded" if not specified

See <a href="https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase">Pod Phase</a>

## ioConfig

### ioConfig.S3_ENDPOINT

S3 endpoint of server to connect to

### ioConfig.S3_REGION

Region S3 server is located

### ioConfig.S3_ACCESS_KEY_ID

Access key to use when connecting to S3 server

### ioConfig.S3_SECRET_ACCESS_KEY

Secret access key to use with access key ID for connecting to S3 server

### ioConfig.USE_SSL

Flag to use SSL when downloading. Defaults to "true"

## engineConfig

Map of environment variables to pass to engine.
See <a href="config">Config</a>

## tests

### tests.pvc

PersistentVolumeClaim where tests are stored in

### tests.mountPath

Path to mount tests PVC to in Cicada engine

Defaults to `/tests`

### tests.remotePath

Path to remotely stored tests. Allows for the following forms:

* S3 path: `s3://bucket/path/to/file(s)`
* Git path: `git://org/repo.git/path/to/tests?protocol=https&branch=master`

Note: S3 path is copied recursively
Note: Git branch defaults to master
Note: Git protocol defaults to `https`. Valid values are:

* `http`
* `https`
* `ftp`
* `ftps`
* `git`
* `ssh`

### tests.localPath

Path to download tests to in IO initializer

Defaults to `/{pvc}`

## reports

### reports.pvc

PersistentVolumeClaim to store reports in

### reports.mountPath

Path to mount reports PVC to in Cicada engine

Defaults to `/reports`

### reports.remotePath

Remote path to upload reports to. Allows for the following forms:

* S3 path: `s3://bucket/path/where/files/should/be`

Note: Files are copied from the directory recursively

### reports.localPath

Path in IO Initializer to upload reports from

Defaults to `/{pvc}`
