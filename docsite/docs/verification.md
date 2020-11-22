---
id: verification
title: Verification
sidebar_label: Verification
---

A verification container can be used to verify the results of a Cicada test run.

The verification container can load a JSON state file from a local path or S3
and returns an exit code `0 ` if all tests ran successfully, or `1` otherwise.

To run the verification container, run:

```bash
docker run --rm -v /path/to/reports:/input cicadatesting/cicada-verification
```

By default, This will run verification against the `state.final.json` file
outputted by the cicada engine to a `reports` directory.

## Verify Tests

### state-file

Option to override the state file to verify.

Example:

```bash
docker run ... cicadatesting/cicada-verification --state-file s3://reports/state.final.json
```

This will load the state file from S3 at `s3://reports/state.final.json`

Currently, this supports the following formats:

* File path: `file:///absolute/path/to/state/file`
* S3 path: `s3://path/to/state/file`

Defaults to `file:///input/state.final.json`

### timeout

Option to override retry time for state file to be loaded

Example:

```bash
docker run ... cicadatesting/cicada-verification --timeout 300
```

This will override the timeout to wait `300` seconds before stopping if the
file can't be found

Defaults to `120` seconds (with `5` seconds between polls)

## Environment variables

### S3_ENDPOINT

S3 endpoint of server to connect to

### S3_REGION

Region S3 server is located

### S3_ACCESS_KEY_ID

Access key to use when connecting to S3 server

### S3_SECRET_ACCESS_KEY

Secret access key to use with access key ID for connecting to S3 server

### USE_SSL

Flag to use SSL when downloading. Defaults to `true`
