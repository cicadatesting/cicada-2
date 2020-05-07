import time

import kafka
from kafka import errors


def main():
    for i in range(3):
        print("sleeping")
        time.sleep(1)

    print("ready to create clients")

    # consume message off stream
    consumer = kafka.KafkaConsumer(
        "inbound-files", bootstrap_servers=["kafka:9092"]
    )

    producer = kafka.KafkaProducer(
        bootstrap_servers=["kafka:9092"]
    )

    for message in consumer:
        print("%s:%d:%d: key=%s value=%s" % (
            message.topic,
            message.partition,
            message.offset,
            message.key,
            message.value)
        )

        producer.send("outbound-files", key=b"fizz", value=b"buzz")


if __name__ == "__main__":
    main()
