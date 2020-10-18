---
id: runners
title: Runners
sidebar_label: Runners
---

Actions and Asserts are performed by runners. Runners perform interactions with
other services and report back to the engine. Each runner is a gRPC server
running in a Docker container that implements the interface below. A test can
only have one type of runner but can have multiple instances of that runner.

```proto
service Runner {
    rpc Action (ActionRequest) returns (ActionReply);
    rpc Assert (AssertRequest) returns (AssertReply);
    rpc Healthcheck (google.protobuf.Empty) returns (HealthcheckReply);
}
```

## Action

A runner must implement an `Action` endpoint that takes an `ActionRequest`
and returns an `ActionReply`

```proto
message ActionRequest {
    string type = 1;
    string params = 2; // JSON string
}

message ActionReply {
    string outputs = 1; // JSON string
}
```

An `ActionRequest` contains the [action type](action.md#type) and
[params](action.md#params) being supplied to the runner.

The parameter `params` in `ActionRequest` is the JSON of the action's `params`
converted to a string.

For example, given this action:

```yaml
actions:
  - type: SomeAction
    params:
      foo: bar
```

The message will look like:

```json
{
    "type": "SomeAction",
    "params": "{\"foo\": \"bar\"}"
}
```

Likewise, the parameter `outputs` in `ActionReply` JSON string of the object
that the runner is returning to the engine.

## Assert

A runner must also implement the `Assert` endpoint taking an
`ActionRequest` and returning an `ActionReply`. In general,
The `Assert` is an extension of an `Action` that checks it's
results in a way specific to the runner's medium of communication.

```proto
message AssertRequest {
    string type = 1;
    string params = 2;
}

message AssertReply {
    bool passed = 1;
    string actual = 2;
    string expected = 3;
    string description = 4;
}
```

Like in `ActionRequest`, the `AssertRequest` contains the
[assert type](assert.md#type) and [params](assert.md#params)
being supplied to the runner. The params are also a JSON string.

Each `AssertReply` contains 4 parameters:

* `passed`: Whether or not the assert passed
* `actual`: The actual data gathered by the runner for the assert
* `expected`: The data expected to be found by the runner in the assert
* `description`: User friendly description summarizing the results of the assert

## Healthcheck

The gRPC server must implement a `healthcheck` endpoint which the engine
can call to ensure it is ready to receive messages.

```proto
message HealthcheckReply {
    bool ready = 1;
}
```

The `healthcheck` endpoint receives an empty call and returns a status
indicating it is ready. The engine will call the healthcheck endpoint
in an exponential backoff which is [configurable](config.md#healthcheck_initial_wait) 
