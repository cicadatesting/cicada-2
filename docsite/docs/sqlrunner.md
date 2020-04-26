---
id: sql-runner
title: SQL Runner
sidebar_label: SQL Runner
---

SQL runnners are used to make sql queries against databases. Currently, Postgres
is supported.

## Config

<pre><code>
config:
  connectionString: string
  driver: string
  username: string
  password: string
  host: string
  port: string
  database: string
</code></pre>

### Connection String

Connection string to use when connecting to database. Must be of the following format:

`{driver}://{username}:{password}@{host}:{port}/{database}`

### Driver

Database driver to use. Currently supported:

* `postgresql`

`REQUIRED` if `connectionString` is not set

### Username

Username to use when authenticating to database

`REQUIRED` if `connectionString` is not set

### Password

Password to use when connecting to database

`REQUIRED` if `connectionString` is not set

### Host

Host name of database

`REQUIRED` if `connectionString` is not set

### Port

Port database is running on

`REQUIRED` if `connectionString` is not set

### Database

Database schema to connect to

`REQUIRED` if `connectionString` is not set

## Actions

<pre><code>
type: <a href="#supported-action-types">string</a>
params:
  query: <a href="#query">string</a>
</code></pre>

Returns

```python
{
    "rows": [
        {
            "column_name": ...,
            "another_column_name": ...
        }
    ]
}
```

### Supported Action Types

* SQLQuery

### Action Params

#### Query

SQL query string to be used by runner

## Asserts

<pre><code>
type: <a href="#supported-assert-types">string</a>
params:
  method: <a href="#supported-action-types">string</a>
  actionParams: <a href="#action-params">Map</a>
  expected: <a href="#expected">List[Map]</a>
</code></pre>

### Supported Assert Types

* ContainsRows: Checks that result contains all of the expected rows
* EqualsRows: Checks that result rows equal the expected rows

### Assert Params

#### Expected

List of Maps, each representing a row where the keys are the column names
