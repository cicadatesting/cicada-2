---
id: action
title: Action
sidebar_label: Action
---

<pre><code>
actions:
  - type: <a href="#type">string</a> (required)
    name: <a href="#name">string</a>
    template: <a href="#template">string</a>
    executionsPerCycle: <a href="#executions-per-cycle">int</a>
    secondsBetweenExecutions: <a href="#seconds-between-executions">float</a>
    storeVersions: <a href="#store-versions">bool</a>
    params: <a href="#params">Map</a>
    outputs: List[<a href="#outputs">Output</a>]
    asserts: List[<a href="#asserts">Assert</a>]
</code></pre>


## Action Params

### Type

`REQUIRED` Type of action (See runner's supported action types)

### Name

Name of action. If not specified, it will be inferred from the runner's type.

### Template

Template string to be rendered into action using the state container

### Execution Per Cycle

Number of times for each runner to execute the action during one cycle.

Defaults to `1` execution per cycle

### Seconds Between Executions

Number of seconds to wait between each execution for a particular action.

Defaults to `0`

### Store Versions

Store all results of an action in the state container. If `false`, will overwrite
the last result and store action results as a single value instead of a list.

Defaults to `true`

### Params

Parameters to provide to action (See runner's supported action params)

### Outputs

Outputs are used to store extra information from an action call (like an index
value or the length of a list returned in action).

The `value` is stored under the `output` section of the action in the state
container. `value` is stored as a list if `storeVersions` is set to `true` (
Defaults to `false`)

```yaml
outputs:
  - name: string (REQUIRED)
    template: string
    storeVersions: bool
    value: Any (REQUIRED)
```

### Asserts

Asserts that run based on the results of the action. JSON returned by runner
is compared against element in `expected` section.

Result of action is available to `template` section under the key `result`.
Example:

```yaml
action:
  ...
  asserts:
    - expected: 5
      template: >
        actual: {{ result['items']|length }}
```

See [Asserts](assert.md) for more information.
