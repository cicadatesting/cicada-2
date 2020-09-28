# Cicada 2

## Overview

Cicada is a tool for automating functional, or black-box style tests
on multiple microservices using gRPC and containerized runners.
It currently supports testing for REST API's and Postgres databases.

## Links

* <a href="https://cicadatesting.github.io/cicada-2/">Documentation</a>

## Running

Cicada uses Docker images for the engine and each of the runners.
The images can be compiled using the Makefile:

```bash
make build-engine

make build-runner RUNNER_NAME=rest-runner
make build-runner RUNNER_NAME=...
```

The build commands for runners will reference a dockerfile
in the `dockerfiles` folder through the `RUNNER_NAME` variable

In addition, you can start up a Docker environment to with all the
required dependencies to play around in:

```bash
make build-env
make run-env
```

This will mount the current directory in a docker container which
will reflect code changes in real time.

### Example Tests

Examples of Cicada in action can be found in the `example_services`
folder. Enter the folder and launch the test using the example's
Makefile:

```bash
cd example_services/rest_api

make run

make clean
```

Note that you may need to build the service's image so it will
work in the example's docker compose pipeline.
