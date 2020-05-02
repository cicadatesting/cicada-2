import time
from datetime import datetime
from typing import List, Optional
from typing_extensions import TypedDict

from kafka import KafkaConsumer, KafkaProducer

from cicada2.shared.asserts import assert_dicts
from cicada2.shared.types import AssertResult


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


def run_action(action_type: str, params: ActionParams) -> ActionResponse:

    if action_type == "Send":
        # TODO: support username password auth
        producer = KafkaProducer(
            bootstrap_servers=params["servers"],
            key_serializer=lambda k: k.encode(params.get("key_encoding", "utf-8")),
            value_serializer=lambda v: v.encode(params.get("value_encoding", "utf-8")),
        )

        failed_messages = []
        start = datetime.now()

        for message in params.get("messages", []):
            topic = message.get("topic") or params["topic"]
            key = message.get("key") or params.get("key")
            value = message["value"]

            def errback(err):
                print(err)
                failed_messages.append(err)

            producer.send(
                topic=topic,
                key=key,
                value=value
            ).add_errback(errback)

        end = datetime.now()
        producer.close()

        return ActionResponse(
            messages_sent=len(params.get("messages")) - len(failed_messages),
            messages_received=None,
            errors=failed_messages,
            runtime=int((end - start).microseconds / 1000),
        )
    elif action_type == "Receive":
        # TODO: group id
        consumer = KafkaConsumer(
            params["topic"],
            bootstrap_servers=params["servers"],
            key_deserializer=lambda k: k.decode(params.get("key_encoding", "utf-8")),
            value_deserializer=lambda v: v.decode(params.get("value_encoding", "utf-8")),
            auto_offset_reset=params.get("offset", "earliest")
        )

        start = datetime.now()
        received_messages = consumer.poll(
            timeout_ms=params.get("timeout_ms", 5000),
            max_records=params.get("max_records")
        )

        end = datetime.now()
        consumer.close()  # NOTE: possibly wrap with `with` clause

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

    print(f"Assert type: {assert_type}")
    print(f"Params: {params}")

    if assert_type == "FindMessage":
        messages = run_action("Receive", params["actionParams"])

        for message in messages["messages_received"]:
            print(f"received message: {message}")

            if assert_dicts(params["expected"], message):
                return AssertResult(
                    actual=str(message),
                    expected=str(params["expected"]),
                    passed=True,
                    description="passed"
                )

        return AssertResult(
            actual=None,
            expected=str(params["expected"]),
            passed=False,
            description=f"No message found matching {params['expected']}"
        )

    raise ValueError(f"Assert type {assert_type} is invalid")
