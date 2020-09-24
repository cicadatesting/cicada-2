---
id: quickstart
title: Quickstart
sidebar_label: Quickstart
---

Cicada requires Docker to run and is available as a Docker image:

```bash
docker pull jeremyaherzog/cicada-2-engine:latest
```

## Running `Cicada`

### Configuring the network

To run Cicada, you'll need to configure a network for the runners to operate in:

```bash
docker network create cicada
```

By default, Cicada uses the `cicada` network. You can also override the
network by providing the `CONTAINER_NETWORK` environment variable.

> If the network does not exist, Cicada will attempt to create it, 
> unless the `CREATE_NETWORK` variable is set to `false`

See [config](config.md) for available environment variables

### Creating a test

Create a folder called `tests` and add a file called `test.cicada.yaml` to it:

```yaml
description: Example test
tests:
  - name: check-google
    description: Checks the status of the Google homepage
    runner: rest-runner
    asserts:
      - type: StatusCode
        params:
          method: GET
          actionParams:
            url: https://google.com
          expected: 200
```

This test will make a call to the Google home page and assert that it receives
a `200` status code


### Starting the engine

Once your system is configured, you can start the container. Make sure to
add it to the `network` and mount the following volumes:

* Docker socket (usually at `/var/run/docker.sock`)
* Tests directory -> Where your `*.cicada.yaml` files are located
* Reports directory -> Where you want the reports generated to

```bash
docker run --rm \
    --name cicada-engine \
    --network cicada \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(pwd)/tests:/tests \
    -v $(pwd)/reports:/reports \
    jeremyaherzog/cicada-2-engine
```

When this finishes running, check the `report.md` file to see the results
