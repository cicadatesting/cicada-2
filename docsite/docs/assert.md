---
id: assert
title: Assert
sidebar_label: Assert
---

<pre><code>
asserts:
  - type: <a href="#type">string</a> (required)
    executionsPerCycle <a href="#executions-per-cycle">string</a>
    name: <a href="#name">string</a>
    template: <a href="#template">string</a>
    storeVersions: <a href="#store-versions">bool</a>
    params: <a href="#params">Map</a>
    keepIfPassed: <a href="#keep-if-passed">bool</a>
    passed: <a href="#passed">bool</a>
    actual: <a href="#actual">string</a>
    expected: <a href="#expected">string</a>
    description: <a href="#description">string</a>
    assertOptions: <a href="#assert-options">string</a>
</code></pre>

Returns

```python
{
    "passed": bool
    "description": str,
    "expected": str,
    "actual": str
}
```

## Assert Params

### Type

`REQUIRED` Type of assert (See runner's supported assert types)

> ### NullAssert
> If `type` is set to `NullAssert`, the assert results will be populated with
> the provided values for <a href="#passed">`passed`</a>, <a href="#actual">`actual`</a>,
> <a href="#expected">`expected`</a>, and <a href="#description">`description`</a>

### Executions Per Cycle

Number of times to execute the assert on a single runner in one cycle. Defaults
to `1`.

### Name

Name of assert. If not specified, it will be inferred from the runner's type.

### Template

Template string to be rendered into assert using the state container

### Store Versions

Store all results of an assert in the state container. If `false`, will overwrite
the last result and store assert results as a single value instead of a list.

Defaults to `true`

### Params

Parameters to provide to assert (See runner's supported action params)

### Keep if Passed

Test will continue running with this assert even if it has passed if set to `false`.

Defaults to `true`

### Actual

Sets assert result's `actual` value to the one provided is using a <a href="#nullassert">`NullAssert`</a>

### Expected

Sets assert result's `expected` value to the one provided is using a <a href="#nullassert">`NullAssert`</a>

### Passed

Sets assert result's `passed` value to the one provided is using a <a href="#nullassert">`NullAssert`</a>

### Description

Sets assert result's `description` value to the one provided is using a <a href="#nullassert">`NullAssert`</a>

## Assert Options

Flags passed as keyword arguments to call assert logic with for an
Assert inside of an Action

<pre><code>
assertOptions:
  match: <a href="#match">bool</a>
  all_required: <a href="#all-required">bool</a>
  ordered: <a href="#ordered">bool</a>
</code></pre>

### Match

If true, allows strings to match a regex instead of an exact string

### All Required

If true, expects all elements in an expected dictionary to be present in
the actual dictionary

### Ordered

If true, requires elements in an expected sequence to be in the same order as
the actual sequence.
