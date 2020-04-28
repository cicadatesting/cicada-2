---
id: tests
title: Tests
sidebar_label: Tests
---

Tests are the main object that Cicada processes. Tests are composed of a single
runner and can depend on other tests.

## Runners

Each test uses a type of runner to execute Actions and Asserts. These runners
exist as Docker containers and communicate with the test engine through gRPC.

Let's take a look at this example:

`test-example.cicada.yaml`:

```yaml
description: Example test
tests:
  - name: add-member
    description: Creates a member
    runner: rest-runner
    actions:
      - type: POST
        params:
          url: "http://api:8080/members"
          body:
            name: Jeff
            age: 25
```

This test uses the `rest-runner` type, used against REST API's, to make a POST
request to an API and create a member named `jeff` age `25`

## Dependencies

All of your tests in `*.cicada.yaml` files will be loaded recursively from a
root directory into a DAG (Directed Acyclic Graph) and processed in parallel
keeping order of their dependencies.

Let's add some more tests with dependencies to our example:

`test-example.cicada.yaml`:

```yaml
description: Example test with dependencies
tests:
  - name: add-member
    description: Creates a member
    runner: rest-runner
    actions:
      - type: POST
        params:
          url: "http://api:8080/members"
          body:
            name: Jeff
            age: 25
  - name: add-team
    description: Creates a team
    runner: rest-runner
    actions:
      - type: POST
        params:
          url: "http://api:8080/teams"
          body:
            name: The best team
  - name: add-jeff-to-team
    description: Adds Jeff to a team
    runner: rest-runner
    action:
      - type: POST
        params:
          url: "http://api:8080/team-members"
          body:
            member: Jeff
            team: The best team
    dependencies:
      - add-member
      - add-team
  - name: check-jeff-added
    description: Checks that a team-member entry was added
    dependencies:
      - add-jeff-to-team
    runner: sql-runner
    assert:
      - type: EqualsRows
        template: >
          params:
            method: SQLQuery
            expected:
            rows:
              - cnt: 1
            actionParams:
              query: >
                SELECT COUNT(*) AS cnt FROM team_members
                WHERE member_uid={{ state['add-member']['actions']['POST0']['results'][0]['body']['id'] }}
                AND team_uid={{ state['add-team']['actions']['POST0']['results'][0]['body']['id'] }}
```

This adds 3 more tests:

* `add-team`: Creates a team through the API
* `add-jeff-to-team`: Adds Jeff to a team and depends on `add-member` and `add-team`
* `check-jeff-added`: Checks that a team_member row has been inserted and depends on `add-jeff-to-team`

> There's also a template section in `check-jeff-added`. This uses the engine's state container
> to format the assertion using Jinja2 into YAML. More on that [later.](state.md)

Cicada will load all of the tests and create this DAG:

```
                add-member            add-team
                    \                    /
                     \                  /
                      \________________/
                                |
                                |
                        add-jeff-to-team
                                |
                                |
                        check-jeff-added
```

<!--TODO: diagram to ascii with automatic center aligned code-->

In this scenario, `add-member` and `add-team` can run in parallel, while
`add-jeff-to-team` waits. Once both tests have finished, `add-jeff-to-team`
will run, followed by `check-jeff-added`
