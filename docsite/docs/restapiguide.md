---
id: rest-api-guide
title: REST API Guide
sidebar_label: REST API Guide
---

In this guide, you'll create tests for an example REST API written with Flask.

[Source code](https://github.com/herzo175/cicada-2/tree/master/example_services/rest_api)

## App

Here we have a simple API that connects to a Postgres database and has one
endpoint, which creates members given a member name as JSON.

`app.py`

```python
from flask import Flask, request, jsonify
from sqlalchemy import create_engine


app = Flask(__name__)
engine = create_engine("postgresql://postgres:admin@db:5432/postgres")


@app.route("/members", methods=["POST"])
def members():
    body = request.json

    with engine.connect() as connection:
        row = list(
            connection.execute(
                "INSERT INTO members (name) VALUES (%s) RETURNING *", body["name"]
            )
        )[0]

    return jsonify({"id": row.id, "name": row.name})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
```

`requirements.txt`

```txt
flask
psycopg2
sqlalchemy
```

## Environment

Next, we'll need to set up our environment using Docker compose. Docker compose
will handle creating the Docker image from a Dockerfile and starting the API
as well as the Postgres database. We'll also want to create our schema for the
database using a migration manager like 'Flyway'

`V1__Initial.sql`

```sql
CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    name TEXT
)
```

`Dockerfile`

```Dockerfile
FROM python:3.8-buster

WORKDIR /app

RUN apt-get update
RUN apt-get install -y libpq-dev python-dev

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app.py .

ENTRYPOINT ["python", "app.py"]
```

`docker-compose.yml`

```yaml
version: '3'
services:
  db:
    image: postgres:12-alpine
    environment:
      - POSTGRES_PASSWORD=admin
    ports:
      - 5432:5432
  flyway:
    image: flyway/flyway:6-alpine
    command: -url=jdbc:postgresql://db:5432/ -schemas=public -user=postgres -password=admin -connectRetries=60 migrate
    volumes:
      - .:/flyway/sql
    depends_on:
      - db
  api:
    build: .
    ports:
      - 8080:8080
    depends_on:
      - db
      - flyway
```

Ensure that the API is built and run successfully with `docker-compose up` or by
running `make run` if using the provided Makefile in the guide

## Tests

Next, we'll want to create tests for our app. Create a file called
`test.cicada.yaml` to house the tests in and add a test that creates 100 members
through the API endpoint:

`test.cicada.yaml`

```yaml
description: Example test
tests:
  - name: add_members
    description: add 100 new members
    runner: rest-runner
    actions:
      - type: POST
        executionsPerCycle: 100
        params:
          url: "http://api:8080/members"
          body:
            name: jeff
```

Next, add the following to `docker-compose.yml` to start Cicada and start
docker-compose again:

`docker-compose.yml`

```yaml
version: '3'
services:
  ...
  cicada:
    image: jeremyaherzog/cicada-2-engine
    environment:
      - CONTAINER_NETWORK=rest_api_default
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - .:/tests
      - ./reports:/reports
    depends_on:
      - api
```

The test should now create 100 users.

Let's add a SQL runner to our test. In this example, we are going to change the
name of all the members in the database. In `test.cicada.yaml`:

`test.cicada.yaml`

```yaml
tests:
  ...
- name: update_ages
    description: update ages of new members
    runner: sql-runner
    dependencies:
      - add_members
    config:
      connectionString: postgresql://postgres:admin@db:5432/postgres
    actions:
      - type: SQLQuery
        params:
          query: "delete from members where name='jeff2'"
      - type: SQLQuery
        template: >
          params:
            {% set ids = [] %}
            {% for member in state['add_members']['actions']['POST0']['results'] if member is not none %}
            {% do ids.append(member['body']['id']) %}
            {% endfor %}
            query: "update members set name='jeff2' where id in ({{ ids|join(',') }})"
```

After updating `test.cicada.yaml`, run docker-compose again. You should be able
to verify in the database that the name of all the members is now `jeff2`.

Finally, we'll want to automate the verification of all the changed members.
Add the following to the test file:

`test.cicada.yaml`

```yaml
tests:
  ...
- name: update_ages
    ...
    asserts:
      - type: EqualsRows
        params:
          method: SQLQuery
          actionParams:
            query: "select count(*) as cnt from members where name='jeff2'"
          expected:
            rows:
              - cnt: 100
```

This will perform a SQL query which will check that 100 users exist in the
database with `name=jeff2`

Run the docker-compose one last time. This test should finish and you will be
able to see the test results in `reports/report.md`

Congratulations! You were able to create and test a REST API!
