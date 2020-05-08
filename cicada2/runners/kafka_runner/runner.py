from os import getenv
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional
from typing_extensions import TypedDict

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

from cicada2.shared.asserts import assert_dicts
from cicada2.shared.types import AssertResult
from cicada2.shared.logs import get_logger


LOGGER = get_logger()


class KafkaMessage(TypedDict):
    topic: Optional[str]
    key: Optional[str]
    value: str


class ActionParams(TypedDict):
    servers: List[str]
    topic: str
    timeout_ms: Optional[int]
    max_records: Optional[int]
    key_encoding: Optional[str]
    value_encoding: Optional[str]
    key: Optional[str]
    messages: Optional[List[KafkaMessage]]
    offset: Optional[str]


class ActionResponse(TypedDict):
    messages_sent: Optional[int]
    messages_received: Optional[List[KafkaMessage]]
    errors: Optional[List[str]]
    runtime: int


class AssertParams(TypedDict):
    actionParams: ActionParams
    expected: KafkaMessage


def extract_auth_parameters() -> Dict[str, str]:
    return {
        "security_protocol": getenv("RUNNER_SECURITY_PROTOCOL", "PLAINTEXT"),
        "sasl_mechanism": getenv("RUNNER_SASL_MECHANISM"),
        "sasl_plain_username": getenv("RUNNER_SASL_USERNAME"),
        "sasl_plain_password": getenv("RUNNER_SASL_PASSWORD"),
        "sasl_kerberos_service_name": getenv("SASL_KERBEROS_SERVICE_NAME", "kafka"),
        "sasl_kerberos_domain_name": getenv("SASL_KERBEROS_DOMAIN_NAME"),
        "sasl_oauth_token_provider": getenv("SASL_OAUTH_TOKEN_PROVIDER"),
    }


@contextmanager
def configure_consumer(topic: str, offset: str) -> KafkaMessage:
    bootstrap_servers = [
        server.strip() for server in getenv("RUNNER_SERVERS").split(",")
    ]
    key_encoding = getenv("RUNNER_KEY_ENCODING", "utf-8")
    value_encoding = getenv("RUNNER_VALUE_ENCODING", "utf-8")

    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            key_deserializer=lambda k: k.decode(key_encoding),
            value_deserializer=lambda v: v.decode(value_encoding),
            auto_offset_reset=offset,
            **extract_auth_parameters(),
        )
    except KafkaError as err:
        raise RuntimeError(f"Unable to create kafka consumer: {err}")

    try:
        yield consumer
    finally:
        consumer.close()


@contextmanager
def configure_producer() -> KafkaProducer:
    LOGGER.debug("runner servers: %s", getenv("RUNNER_SERVERS"))

    bootstrap_servers = [
        server.strip() for server in getenv("RUNNER_SERVERS").split(",")
    ]
    key_encoding = getenv("RUNNER_KEY_ENCODING", "utf-8")
    value_encoding = getenv("RUNNER_VALUE_ENCODING", "utf-8")

    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            key_serializer=lambda k: k.encode(key_encoding),
            value_serializer=lambda v: v.encode(value_encoding),
            **extract_auth_parameters(),
        )
    except KafkaError as err:
        raise RuntimeError(f"Unable to create kafka producer: {err}")

    try:
        yield producer
    finally:
        producer.close()


def run_action(action_type: str, params: ActionParams) -> ActionResponse:
    LOGGER.debug("Called run action with params: %s", params)

    if action_type == "Send":
        with configure_producer() as producer:
            failed_messages = []
            start = datetime.now()

            for message in params.get("messages", []):
                topic = message.get("topic") or params["topic"]
                key = message.get("key") or params.get("key")
                value = message["value"]

                def errback(err):
                    LOGGER.warning("Error sending message: %s", err)
                    failed_messages.append(err)

                producer.send(topic=topic, key=key, value=value).add_errback(errback)

            producer.flush()
            end = datetime.now()

            return ActionResponse(
                messages_sent=len(params.get("messages")) - len(failed_messages),
                messages_received=None,
                errors=failed_messages,
                runtime=int((end - start).microseconds / 1000),
            )
    elif action_type == "Receive":
        with configure_consumer(
            params["topic"], params.get("offset", "earliest")
        ) as consumer:
            start = datetime.now()

            received_messages = consumer.poll(
                timeout_ms=params.get("timeout_ms", 5000),
                max_records=params.get("max_records"),
            )

            end = datetime.now()

            return ActionResponse(
                messages_sent=None,
                messages_received=[
                    KafkaMessage(topic=params["topic"], key=msg.key, value=msg.value)
                    for msg_list in received_messages.values()
                    for msg in msg_list
                ],
                errors=None,
                runtime=int((end - start).microseconds / 1000),
            )
    else:
        raise ValueError(f"Action type {action_type} is invalid")


def run_assert(assert_type: str, params: AssertParams) -> AssertResult:

    if assert_type == "FindMessage":
        messages = run_action("Receive", params["actionParams"])

        for message in messages["messages_received"]:
            if assert_dicts(params["expected"], message):
                return AssertResult(
                    actual=str(message),
                    expected=str(params["expected"]),
                    passed=True,
                    description="passed",
                )

        return AssertResult(
            actual=None,
            expected=str(params["expected"]),
            passed=False,
            description=f"No message found matching {params['expected']}",
        )

    raise ValueError(f"Assert type {assert_type} is invalid")
