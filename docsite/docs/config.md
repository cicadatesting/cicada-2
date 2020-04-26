---
id: config
title: Config
sidebar_label: Config
---

Environment variables that can be provided to the engine

## CONTAINER_NETWORK

Docker network to attach containers to.

Defaults to `cicada-2`

## CREATE_NETWORK

Create `CONTAINER_NETWORK` if set to `true`, `y`, or `yes`

Defaults to `true`

## HEALTHCHECK_INITIAL_WAIT

Time in seconds to wait before checking runner for first time before entering exponential backoff

Defaults to `2` seconds

## HEALTHCHECK_MAX_RETRIES

Amount of times to try healthchecking runner

Defaults to `5` tries

## INITIAL_STATE_FILE

Path to JSON state file to use as the inital state data to provide to tests.
Must also be mounted to engine in a volume.

## REPORTS_FOLDER

Path in engine to write reports files to.

Defaults to `/reports`

## TASK_TYPE

Container platform to use for runners.

Only supported value (and default) is `docker` (Kubernetes coming some day)

## TESTS_FOLDER

Path in engine to load test files from.

Defaults to `/tests`
