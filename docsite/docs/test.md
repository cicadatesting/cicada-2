---
id: test
title: Test
sidebar_label: Test
---

<pre><code>
tests:
  - name: <a href="#name">string</a> (required)
    timeout: <a href="#timeout">float</a>
    runIfFailedDependency: <a href="#run-if-failed-dependency">bool</a>
    cycles: <a href="#cycles">cycles</a>
    description: <a href="#description">string</a>
    runner: <a href="#runner">string</a>
    runnerCount: <a href="#runner-count">int</a>
    image: <a href="#image">string</a>
    volumes: List[<a href="#volume">Volume</a>]
    config: <a href="#config">Map</a>
    secondsBetweenCycles: <a href="#seconds-between-cycles">float</a>
    secondsBetweenActions: <a href="#seconds-between-actions">float</a>
    secondsBetweenAsserts: <a href="#seconds-between-asserts">float</a>
    actionDistributionStrategy: <a href="#distribution-strategy">string</a>
    assertDistributionStrategy: <a href="#distribution-strategy">string</a>
    actions: List[<a href="action">Action</a>]
    asserts: List[<a href="assert">Assert</a>]
    dependencies: List[<a href="#dependencies">string</a>]
</code></pre>

## Test Params

### Name

`REQUIRED` Name of test. Must be unique. Used to identify test in engine.

### Timeout

Time in seconds test must finish in before ending it. By default, the timeout is
set to 15 seconds, but can be set to a negative value for an infinite timeout.

### Run If Failed Dependency

If one of the specified dependencies has failed, still run this test.
By default, tests are skipped if they have failed dependencies

### Cycles

Sets a limit on the number of times to run through all the specified asserts and
actions. If set to a negative number, the number of cycles is unlimited.

Suppose we had a test with two actions and `cycles` was set to 3:

```
cycles: 3
actions:
  - type: POST
    name: foo
    ...
  - type: POST
    name: bar
```

The test would through the actions list 3 times, calling `foo` 3 times and `bar`
3 times for a total of 6 action calls.

Now, say we had 2 asserts in this test in addition to the two actions:

```
cycles: 3
actions:
  - type: POST
    name: foo
    ...
  - type: POST
    name: bar
    ...
asserts:
  - type: JSON
    name: fizz
    ...
  - type: StatusCode
    name: buzz
    ...
```

The test would run `foo` and `bar`, then run `fizz` and `buzz`.
If both asserts pass, the test would finish and continue onto the next.
However, if at least one assert remains, the test will run `foo` and `bar` again,
and then run the remaining assert(s), until the test has cycled through up to 3 times.

At most, each action and assert would be run 3 times, or until the test reaches it's timeout.
You can ensure the test runs each action and assert 3 times by [not removing the
asserts if they pass](assert.md#keep-if-passed).

By default, if there are only actions, `cycles` is set to 1. If there are asserts,
`cycles` is set to -1. Otherwise (no action or asserts), the test will not run anything.

### Description

String describing test

### Runner

Type of runner this test is being run with

### Runner Count

Number of runners to use in test

### Image

Run this Docker image if runner is not specified

### Volume

Allows a host directory to be mounted to a runner. Has the following structure:

```yaml
source: string
destination: string
```

Where `source` is the absolute path to a directory on the host machine and
`destination` is the path inside the container to attach to.

### Config

Map of parameters to provide to runner. <a href="sql-runner#config">Example</a>

### Seconds Between Cycles

Seconds to wait before repeating the cycle if the test should keep running

### Seconds Between Actions

Seconds for each runner to wait before running the next action in the list

### Seconds Between Asserts

Seconds for each runner to wait before running the next assert in the list

### Distribution Strategy

Determines how to assign actions and asserts to runners. Two strategies are supported, `parallel` and `series`

#### Parallel:

Each runner is given all of the actions or asserts:

```
runnerCount: 2
actions:
  - type: POST
    name: foo
    ...
  - type: POST
    name: bar
    ...
```

In this case, each runner will run `foo` and `bar`, for a total of 4 action calls
(2 calls to `foo` and 2 calls to `bar`)

#### Series:

The actions and asserts are assigned to the actions or asserts in a queue

```
runnerCount: 2
asserts:
  - type: JSON
    name: fizz
    ...
  - type: StatusCode
    name: buzz
    ...
```

In this case, the first runner will run assert `fizz` and the second runner will run assert `buzz`
for a total of 2 assert calls.

By default, `actionsDistributionStrategy` is set to `parallel` and `assertDistributionStrategy` is set to `series`

### Dependencies

Names of tests that must run before this test
