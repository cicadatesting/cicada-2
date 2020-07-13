import importlib
import json
import base64
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import grpc

# from grpc_status import rpc_status
from google.protobuf.json_format import Parse
from google.protobuf.json_format import MessageToDict
from typing_extensions import TypedDict

from cicada2.shared.asserts import assert_element
from cicada2.shared.logs import get_logger
from cicada2.shared.types import AssertResult


LOGGER = get_logger()


class Metadata(TypedDict):
    key: str
    value: str


class ActionParams(TypedDict):
    proto: str
    service: str
    serviceAddress: str
    message: Optional[dict]
    messages: Optional[List[dict]]
    metadata: Optional[List[Metadata]]
    compression: Optional[str]
    method: str
    requestType: str


class ResponseError(TypedDict):
    details: str
    code: str


class ActionResponse(TypedDict):
    response: Optional[Union[dict, List[dict]]]
    metadata: Optional[Dict[str, str]]
    error: Optional[ResponseError]


class AssertParams(TypedDict):
    actionType: str
    actionParams: ActionParams
    expected: Union[
        Optional[Union[dict, List[dict]]],
        Optional[Dict[str, str]],
        Optional[ResponseError],
    ]
    assertOptions: Dict[str, str]


FormattedMetadata = List[Tuple[str, str]]


# TODO: some way to define ActionResponse and GrpcResponse in the same class
GrpcResponse = Tuple[Optional[Union[dict, List[dict]]], Optional[Dict[str, str]]]
GrpcResponseSafe = Tuple[
    Optional[Union[dict, List[dict]]], Optional[Dict[str, str]], Optional[ResponseError]
]


def validate_action_params(params: ActionParams) -> List[str]:
    problems = []

    if "proto" not in params:
        problems.append("must specify 'proto' in action params")

    if "service" not in params:
        problems.append("must specify 'service' in action params")

    if "serviceAddress" not in params:
        problems.append("must specify 'serviceAddress' in action params")

    if "message" not in params and "messages" not in params:
        problems.append("must specify 'message' or 'messages' in action params")

    if "messages" in params and not isinstance(params["messages"], list):
        problems.append("'messages' if specified must be a list")

    if "method" not in params:
        problems.append("must specify 'method' in action params")

    if "requestType" not in params:
        problems.append("must specify 'requestType' in action params")

    return problems


def run_action(action_type: str, params: ActionParams) -> ActionResponse:
    # pylint: disable=unbalanced-tuple-unpacking
    params_problems = validate_action_params(params)

    if params_problems:
        raise ValueError(f"ActionParams invalid: {', '.join(params_problems)}")

    proto = params["proto"]
    service = params["service"]
    service_address = params["serviceAddress"]
    message_body = params.get("message", {})
    message_bodies = params.get("messages", [])
    request_metadata = [(md["key"], md["value"]) for md in params.get("metadata", [])]
    compression = params.get("compression")
    method = params["method"]
    request_type = params["requestType"]

    service_module = importlib.import_module(
        f"incoming_protos.{proto.lower()}_pb2_grpc"
    )
    message_module = importlib.import_module(f"incoming_protos.{proto.lower()}_pb2")

    # Convert value supposed to bytes to base64 string
    # params = base64.b64encode(params.encode('utf-8')).decode('utf-8')

    with grpc.insecure_channel(
        service_address, compression=get_compression_level(compression)
    ) as channel:
        stub = getattr(service_module, f"{service}Stub")(channel)

        method_rpc = getattr(stub, method)
        request_dataclass = getattr(message_module, request_type)

        if action_type == "Unary":
            response, metadata, err = unary_request(
                method_rpc, request_dataclass, message_body, request_metadata
            )
        elif action_type == "ClientStreaming":
            response, metadata, err = client_streaming_request(
                method_rpc, request_dataclass, message_bodies, request_metadata
            )
        elif action_type == "ServerStreaming":
            response, metadata, err = server_streaming_request(
                method_rpc, request_dataclass, message_body, request_metadata
            )
        elif action_type == "BidirectionalStreaming":
            response, metadata, err = bidirectional_streaming_request(
                method_rpc, request_dataclass, message_bodies, request_metadata
            )
        else:
            raise ValueError(f"Action type {action_type} is invalid")

        return ActionResponse(response=response, metadata=metadata, error=err)


def validate_assert_params(params: AssertParams) -> List[str]:
    problems = []

    if "actionType" not in params:
        problems.append("must specify 'actionType' in assert params")

    if "actionParams" not in params:
        problems.append("must specify 'actionParams' in assert params")

    if "expected" not in params:
        problems.append("must specify 'expected' in assert params")

    return problems


def run_assert(assert_type: str, params: AssertParams) -> AssertResult:
    action_type = params["actionType"]
    action_params = params["actionParams"]
    expected = params["expected"]
    assert_options = params.get("assertOptions", {})

    action_result = run_action(action_type, action_params)

    if assert_type == "ResponseAssert":
        actual = action_result["response"]
        passed, description = assert_element(expected, actual, **assert_options)
    elif assert_type == "MetadataAssert":
        actual = action_result["metadata"]
        passed, description = assert_element(expected, actual, **assert_options)
    elif assert_type == "ErrorAssert":
        actual = action_result["error"]
        passed, description = assert_element(expected, actual, **assert_options)
    else:
        raise ValueError(f"Assert type {assert_type} is invalid")

    return AssertResult(
        actual=json.dumps(actual),
        expected=json.dumps(expected),
        passed=passed,
        description=json.dumps(description),
    )


def safe_request(
    func: Callable[[Tuple[Any, ...]], GrpcResponse]
) -> Callable[[Tuple[Any, ...]], GrpcResponseSafe]:
    def wrapper(*args, **kwargs):
        try:
            body, metadata = func(*args, **kwargs)
            return body, metadata, None
        except grpc.RpcError as err:
            LOGGER.error("RPC Error making request: %s", err)

            return None, None, {"details": str(err.details()), "code": str(err.code())}

    return wrapper


@safe_request
def unary_request(
    method_rpc: Any,
    request_dataclass: Any,
    message_body: dict,
    request_metadata: FormattedMetadata = (),
):
    request = Parse(json.dumps(message_body), request_dataclass())
    response, call = method_rpc.with_call(request, metadata=request_metadata)

    return MessageToDict(response), format_metadata(call.trailing_metadata())


@safe_request
def client_streaming_request(
    method_rpc: Any,
    request_dataclass: Any,
    message_bodies: List[dict],
    request_metadata: FormattedMetadata = (),
):
    request_iterator = request_generator(message_bodies, request_dataclass)
    response, call = method_rpc.with_call(request_iterator, metadata=request_metadata)

    return MessageToDict(response), format_metadata(call.trailing_metadata())


@safe_request
def server_streaming_request(
    method_rpc: Any,
    request_dataclass: Any,
    message_body: dict,
    request_metadata: FormattedMetadata = (),
):
    request = Parse(json.dumps(message_body), request_dataclass())
    response = method_rpc(request, metadata=request_metadata)

    return (
        [MessageToDict(response_body) for response_body in response],
        format_metadata(response.trailing_metadata()),
    )


@safe_request
def bidirectional_streaming_request(
    method_rpc: Any,
    request_dataclass: Any,
    message_bodies: List[dict],
    request_metadata: FormattedMetadata = (),
):
    request_iterator = request_generator(message_bodies, request_dataclass)
    response = method_rpc(request_iterator, metadata=request_metadata)

    return (
        [MessageToDict(response_body) for response_body in response],
        format_metadata(response.trailing_metadata()),
    )


def request_generator(message_bodies: List[dict], request_dataclass: Any):
    for message_body in message_bodies:
        yield Parse(json.dumps(message_body), request_dataclass())


def format_metadata(trailing_metadata: List[Tuple[str, str]]) -> dict:
    return {key: make_json_safe(value) for key, value in trailing_metadata}


def make_json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("utf-8")

    return value


def get_compression_level(compression: str) -> grpc.Compression:
    if str(compression).lower() == "deflate":
        return grpc.Compression.Deflate
    elif str(compression).lower() == "gzip":
        return grpc.Compression.Gzip
    else:
        return grpc.Compression.NoCompression
