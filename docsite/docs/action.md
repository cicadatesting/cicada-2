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

<pre><code>
outputs:
  - name: string
    template: string
    storeVersions: bool
    value: Any
</code></pre>

<!-- This is a link to an [external page.](http://www.example.com) -->
