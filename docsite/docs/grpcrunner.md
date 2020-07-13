---
id: grpc-runner
title: gRPC Runner
sidebar_label: gRPC Runner
---

The gRPC runner is used to connect to gRPC services given a proto file
to dynamically create requests with

## Config

The gRPC runner requires protos to be mounted to the `/incoming_protos` folder
inside the runner:

```
volumes:
  - source: /path/to/local/protos
    destination: /incoming_protos
```

## Actions

<pre><code>
type: <a href="#supported-action-types">string</a>
params:
  proto: <a href="#proto">string</a>
  service: <a href="#service">string</a>
  serviceAddress: <a href="#service-address">string</a>
  message: <a href="#message">dict</a>
  messages: List[<a href="#messages">dict</a>]
  metadata: List[<a href="#metadata">Metadata</a>]
  compression: <a href="#compression">string</a>
  method: <a href="#method">string</a>
  requestType: <a href="#requestType">string</a>
</code></pre>

Returns

<pre><code>
{
    response: <a href="#response">Union[dict, List[dict]]</a>
    metadata: [Dict[str, str]]
    error: <a href="#response-error">ResponseError</a>
}
</code></pre>

### Response

Dict or list of dicts received from service on successful response

### Response Error

Details about error if encountered and error code received from server

```
{
    ...
    "error": {
        "details": string,
        "code": string
    }
}
```

### Supported Action Types

* `Unary`: Send one request and receive one response from server
* `ClientStreaming`: Sends multiple messages to server and receives one response
* `ServerStreaming`: Sends one message and receives list of responses from server
* `BidirectionalStreaming`: Sends and receives sequences of messages

### Proto

Name of protobuf to use. For example, if the proto is named `app.proto`, 
the `proto` field should be set to `app`

### Service

Name of the gRPC service to use, such as `Greeter` in the hello world gRPC
example

### Service Address

URL of gRPC server

### Message

Map to be converted into protobuf message. Note, `bytes` type values should
be converted into base64 strings. For example:

`base64.b64encode("my value".encode("utf-8")).decode("utf-8")`

### Messages

List of message body protobufs

### Metadata

List of key value pairs to be sent as metadata for each message in the request:

```
metadata:
  - key: foo
    value: bar
```

In a response body, the metadata is compressed to a simple dict:

```
{
    ...
    "metadata": {
        "foo": "bar"
    }
}
```

### Compression

Compression scheme to apply to messages sent/received in the request. Valid
values:

* `deflate`
* `gzip`

### Method

Function to call service with, such as `SayHello`

### Request Type

Protobuf structure to marshal messages into, such as `HelloRequest`

## Asserts

<pre><code>
type: <a href="#supported-assert-types">string</a>
params:
  actionType: <a href="#supported-action-types">string</a>
  actionParams: <a href="#actions">ActionParams</a>
  expected: <a href="#expected">Expected</a>
  assertOptions: <a href="#assert-options">dict</a>
</code></pre>

### Supported Assert Types

* `ResponseAssert`: Checks the received message body/bodies
* `MetadataAssert`: Checks the metadata
* `ErrorAssert`: Check the error body

### Expected

The expected message body(s), [metadata](#metadata),
or [error](#response-error)

### Assert Options

Keyword arguments to call assert with.
See [assert options](assert#assert-options)
