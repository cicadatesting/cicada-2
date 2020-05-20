---
id: async-app-guide
title: Async App Guide
sidebar_label: Async App Guide
---

In this guide, you'll create tests for a service that receives messages from
a Kafka server and modifies files on S3.

[Source code](https://github.com/herzo175/cicada-2/tree/master/example_services/file_transform_service)

## App

First, we'll need to create a Kafka server and S3 compatible data store. We'll
use minio as the S3 server and docker-compose to start them:

`docker-compose.yml`

```yaml
version: '3'
services:
  zookeeper:
    image: bitnami/zookeeper:latest
    ports:
      - 2181:2181
    environment:
      - ALLOW_ANONYMOUS_LOGIN=yes
  kafka:
    image: bitnami/kafka:latest
    depends_on:
      - zookeeper
    ports:
      - 9092:9092
      - 29092:29092
    environment:
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,PLAINTEXT_HOST://:29092
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
  s3:
    image: minio/minio:latest
    ports:
      - 9000:9000
    command: server /data
    environment:
      - MINIO_REGION_NAME=local
      - MINIO_ACCESS_KEY=EXAMPLE_ACCESS_KEY
      - MINIO_SECRET_KEY=EXAMPLE_SECRET_KEY
```

Run `docker-compose up` to start the services and make sure all 3 are running.

Next, we'll need to create a client that connects to Kafka and S3:

`app.py`

```python
import time

import boto3
import kafka
from kafka.errors import NoBrokersAvailable


def main():
    consumer = None
    producer = None
    sleep_time = 1

    # Exponential backoff to connect to brokers
    for i in range(5):
        try:
            consumer = kafka.KafkaConsumer("inbound-files", bootstrap_servers=["kafka:9092"])
            producer = kafka.KafkaProducer(bootstrap_servers=["kafka:9092"])
            break
        except NoBrokersAvailable:
            print(f"waiting {sleep_time} seconds for brokers")
            time.sleep(sleep_time)
            sleep_time *= 2

    if consumer is None or producer is None:
        raise RuntimeError("Timed out waiting for message brokers")

    print("Connected to brokers!")

    s3_client = boto3.client(
        "s3",
        region_name="local",
        endpoint_url="http://s3:9000",
        aws_access_key_id="EXAMPLE_ACCESS_KEY",
        aws_secret_access_key="EXAMPLE_SECRET_KEY",
    )


if __name__ == "__main__":
    main()
```

```requirements.txt
kafka-python==2.0.1
boto3
pyyaml
```

`Dockerfile`

```Dockerfile
FROM python:3.8-slim-buster

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app.py .

ENTRYPOINT ["python", "-u", "app.py"]
```

`docker-compose.yml`

```yaml
services:
  ...
  service:
    build: .
    depends_on:
      - kafka
```

This app connects to Kafka and S3 specified in the `docker-compose.yml` file
and exits. Run `docker-compose up` again and ensure it exits successfully.

## Tests

Once we can confirm the app can connect to Kafka and S3, it's time to begin
sending messages to it. First, add the following to the app:

`app.py`

```python
...
def main()
    ...
    s3_client = ...

    # consume message off stream and process
    for message in consumer:
        print(
            "%s:%d:%d: key=%s value=%s"
            % (
                message.topic,
                message.partition,
                message.offset,
                message.key,
                message.value,
            )
        )

        producer.send("outbound-files", key=bytes(file_key, "utf-8"))
    ...
```

This will print the contents of a message received in the stream and send a
message to a stream called `outbound-files` with the same message key.

For our test, we will be sending 3 messages to the stream in a batch and
checking that the app processes them successfully.

One way to specify the messages is through the `globals` section of the
state container defined before the test begins. Create a directory called
`test_data` and add a file called `initial.json` to it:

`initial.json`

```json
{
  "globals": {
    "transform_files": ["file_a", "file_b", "file_c"]
  }
}
```

Next, use the globals section (The structure is completely up to the user)
to create a test that sends the messages:

`test.cicada.yaml`

```yaml
description: Example file transform test
tests:
  - name: send-messages
    description: Send a message to service
    runner: kafka-runner
    config:
      servers: kafka:9092
    template: >
      actions:
        {% for tf in state["globals"]["transform_files"] %}
        - type: Send
          params:
            topic: inbound-files
            messages:
              - key: {{ tf }}
        {% endfor %}
      asserts:
        {% for tf in state["globals"]["transform_files"] %}
        - type: FindMessage
          params:
            actionParams:
              topic: outbound-files
            expected:
              key: {{ tf }}
        {% endfor %}
```

Using the `template` section of the test, we can create 3 actions and asserts
for the `transform_files` to send and receive messages from different streams.

Finally, add the following to the docker compose file:

`docker-compose.yml`

```yaml
services:
  ...
  cicada:
    image: jeremyaherzog/cicada-2-engine
    environment:
      - CONTAINER_NETWORK=file_transform_service_default
      - INITIAL_STATE_FILE=/initial-data/initial.json
      - WORKDIR=${WORKDIR}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - .:/tests
      - ./reports:/reports
      - ./test_data:/initial-data
    depends_on:
      - service
```

This will start cicada with the other services and mount the initial data file
in the cicada container as well as tell it to load into state.

Run `docker-compose up` again and ensure cicada runs successfully (by checking
the report in `reports/report.md`)

## Business Logic

Let's add some more functionality to the app. For this use case, we want the
app to receive a message through Kafka, locate a file in S3 with that file key,
and convert it from YAML to JSON.

Add the following to the app:

`app.py`

```python
import json
import yaml

...

def main():
    ...
    for message in consumer:
        ...
        file_key = message.key.decode("utf-8")

        # get file from s3 by key
        file = s3_client.get_object(
            Bucket="file-transform-service", Key=f"{file_key}.yaml"
        )

        contents = file["Body"].read().decode("utf-8")

        # transform file contents (yaml format) to JSON
        mapping = yaml.safe_load(contents)

        # save new file contents and send completed message
        s3_client.put_object(
            Bucket="file-transform-service",
            Key=f"{file_key}.json",
            Body=bytes(json.dumps(mapping), "utf-8"),
        )
...
```

Next, we'll want to seed S3 to make sure there are YAML files available to
the app. We can do this by uploading them through Cicada.

First, create 3 files, `file_a.yaml`, `file_b.yaml`, and `file_c.yaml`. They
should follow this format:

`file_{x}.yaml`

```yaml
foo_{x}: bar_{x}
fizz_{x}: buzz_{x}
```

Next, use Cicada to upload them (place before `send-messages`):

`test.cicada.yaml`

```yaml
tests:
  - name: seed
    description: create test bucket
    runner: s3-runner
    config:
      accessKeyID: EXAMPLE_ACCESS_KEY
      secretAccessKey: EXAMPLE_SECRET_KEY
      region: local
      endpointURL: http://s3:9000
    template: >
      volumes:
        - source: {{ getenv("WORKDIR") }}/test_data
          destination: /test_data
      actions:
        - type: cb
          params:
            bucketName: file-transform-service
        {% for tf in state["globals"]["transform_files"] %}
        - type: put
          params:
            sourcePath: /test_data/{{ tf }}.yaml
            destinationPath: s3://file-transform-service/{{ tf }}.yaml
        {% endfor %}
    ...
```

This will mount the tests into the runner's `test_data` folder (location can be
anywhere user specified) and creates the bucket as well as 3 upload actions
for each of the files.

Finally, we'll want to check that the app creates JSON versions of the input
files. One way of doing this is to create 3 of the expected output files and
compare the ones created to these controls.

Create the following files: `test_a.json`, `test_b.json`, `test_c.json`. They
should follow this format:

`test_{x}.json`

```json
{"foo_{x}": "bar_{x}", "fizz_{x}": "buzz_{x}"}
```

Finally, add an assertion to the test to compare the files:

`test.cicada.yaml`

```yaml
tests:
  ...

  - name: check-file-transform
    description: Check that file has been updated
    runner: s3-runner
    config:
      accessKeyID: EXAMPLE_ACCESS_KEY
      secretAccessKey: EXAMPLE_SECRET_KEY
      region: local
      endpointURL: http://s3:9000
    template: >
      volumes:
        - source: {{ getenv("WORKDIR") }}/test_data
          destination: /test_data
      asserts:
        {% for tf in state["globals"]["transform_files"] %}
        - type: FilesEqual
          params:
            path: s3://file-transform-service/{{ tf }}.json
            expected: /test_data/{{ tf }}.json
        {% endfor %}
    dependencies:
      - send-messages
```

This test will use the template to create 3 `FilesEqual` asserts, one for each
of the expected files.

Once ready, run `docker-compose up`. The asserts should pass, indicating that
the files were uploaded and transformed. You can also double check the files
using the Minio UI.

Excellent! We're almost there! The last step is to clean up our bucket. Simply
add the following to the test file:

`test.cicada.yaml`

```yaml
tests:
    ...
  - name: teardown
    description: Delete temporary S3 bucket
    runner: s3-runner
    config:
      accessKeyID: EXAMPLE_ACCESS_KEY
      secretAccessKey: EXAMPLE_SECRET_KEY
      region: local
      endpointURL: http://s3:9000
    actions:
      - type: rm
        params:
          path: s3://file-transform-service
          recursive: true
    dependencies:
      - check-file-transform
```

This will recursively delete objects in the bucket we created,
`file-transform-service`, including the bucket itself

Once verifying the test finishes successfully and the bucket was removed in the
Minio UI, pat yourself on the back! You successfully created and tested an
asynchronous app!
