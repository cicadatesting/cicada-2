---
id: rest-runner
title: REST Runner
sidebar_label: REST Runner
---

The REST runner is used to make calls to REST API's

## Actions

<pre><code>
type: <a href="#supported-action-types">string</a>
params:
  url: <a href="#url">string</a>
  headers: <a href="#headers">Map[string, string]</a>
  queryParams: <a href="#query-params">Map[string, string]</a>
  body: <a href="#body">Map</a>
  username: <a href="#username">string</a>
  password: <a href="#password">string</a>
</code></pre>

Returns

```python
{
  "status_code": int,
  "headers": Map of headers,
  "body": Map of JSON returned,
  "text": string of JSON returned,
  "runtime": float of request/response time in milliseconds
}
```

### Supported Action Types

* GET
* DELETE
* POST
* PATCH
* PUT

### Action Params

#### URL

URL to make request to

#### Headers

Map of headers, such as `Authorization: Bearer ...`, to provide to request

#### Query Params

Map of query params to add to URL

#### Body

Body to convert to JSON when request is made

#### Username

Username to use if this request requires basic auth

#### Password

Password to use in basic auth

## Asserts

<pre><code>
type: <a href="#supported-assert-types">string</a>
params:
  method: <a href="#supported-action-types">string</a>
  actionParams: <a href="#action-params">Map</a>
  expected: <a href="#expected">int or Map</a>
  allRequired: <a href="#all-required">bool</a>
</code></pre>

### Supported Assert Types

* StatusCode: Checks that the response status code equals expected
* Headers: Checks that the response headers match the expected value
* JSON: Checks that the response body matches the expected value

### Assert Params

#### Expected

Int (for status code) or Map to check against headers or JSON

#### All Required

If set to `true`, each value in the `expected` Map must be present and equal
in the actual response
