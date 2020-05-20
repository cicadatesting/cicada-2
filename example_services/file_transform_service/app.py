import time
import json
import yaml

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

        producer.send("outbound-files", key=bytes(file_key, "utf-8"))


if __name__ == "__main__":
    main()
