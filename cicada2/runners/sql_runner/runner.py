from os import getenv
from typing import Any, List, Tuple
from typing_extensions import TypedDict

from sqlalchemy import create_engine, engine

from cicada2.shared.asserts import assert_dicts
from cicada2.shared.types import AssertResult


Rows = List[dict]


class ActionParams(TypedDict):
    query: str


class ActionResult(TypedDict):
    rows: Rows


class ExpectedAssertData(TypedDict):
    rows: Rows


class AssertParams(TypedDict):
    method: str
    actionParams: ActionParams
    expected: ExpectedAssertData


ENGINE: Any = None


def get_engine() -> engine:
    # TODO: validate connection works, possibly in healthcheck
    global ENGINE

    if ENGINE is not None:
        return ENGINE

    connection_string = getenv("RUNNER_CONNECTIONSTRING")

    if connection_string is not None:
        # NOTE: maybe expect connection string in JDBC format
        ENGINE = create_engine(connection_string)
        return ENGINE

    # TODO: support for mysql, possibly sqllite
    # postgresql://postgres:admin@db:5432/postgres

    driver = getenv("RUNNER_DRIVER")
    username = getenv("RUNNER_USERNAME")
    password = getenv("RUNNER_PASSWORD")
    host = getenv("RUNNER_HOST")
    port = getenv("RUNNER_PORT")
    database = getenv("RUNNER_DATABASE")

    assert None not in [
        driver,
        username,
        password,
        host,
        port,
        database,
    ], """
        Must specify connectionString or the following:
        * username
        * password
        * host
        * port
        * database
        """

    ENGINE = create_engine(f"{driver}://{username}:{password}@{host}:{port}/{database}")
    return ENGINE


def run_action(action_type: str, params: ActionParams) -> ActionResult:
    print(action_type)
    print(params)

    # TODO: param validation
    # TODO: Error catching
    if action_type == "SQLQuery":
        with get_engine().connect() as connection:
            query = params["query"]
            result = connection.execute(query)
    else:
        raise ValueError(f"Action type {action_type} is invalid")

    print(f"{params['query']} returns rows: {result.returns_rows}")

    if result.returns_rows:
        # item[0] is column name
        # item[1] is column value
        # row.items() is list of tuples for the row
        rows = [{item[0]: item[1] for item in row.items()} for row in result]
    else:
        rows = []

    print(rows)

    return {"rows": rows}


def contains_rows(
    expected_rows: List[dict], actual_rows: List[dict]
) -> Tuple[bool, str]:
    remaining_rows = expected_rows[:]

    for actual_row in actual_rows:
        for i, expected_row in enumerate(remaining_rows):
            row_matches, _ = assert_dicts(expected_row, actual_row, all_required=False)

            if row_matches:
                del remaining_rows[i]

    if not remaining_rows:
        passed = True
        description = "passed"
    else:
        passed = False
        # NOTE: may need better formatting
        description = f"The following rows did not match any returned: {remaining_rows}"

    return passed, description


def equals_rows(expected_rows: List[dict], actual_rows: List[dict]) -> Tuple[bool, str]:
    if len(expected_rows) != len(actual_rows):
        description = f"Expected {len(expected_rows)} rows, got {len(actual_rows)}"

        return False, description

    for expected_row, actual_row in zip(expected_rows, actual_rows):
        row_matches, description = assert_dicts(
            expected_row, actual_row, all_required=True
        )

        if not row_matches:
            return False, description

    return True, "passed"


def assert_params_problems(params: AssertParams) -> List[str]:
    problems = []

    if "method" not in params:
        problems.append("Missing 'method' in assert params")

    if "actionParams" not in params:
        problems.append("Missing 'actionParams' in assert params")

    if "expected" not in params:
        problems.append("Missing 'expected' in assert params")

    return problems


def run_assert(assert_type: str, params: AssertParams) -> AssertResult:
    params_problems = assert_params_problems(params)

    if params_problems:
        raise ValueError(f"Params invalid: {', '.join(params_problems)}")

    action_response = run_action(params["method"], params["actionParams"])
    expected = params["expected"]

    print(action_response)

    if assert_type == "ContainsRows":
        # NOTE: possibly validate that expected/action response has rows
        expected_rows = expected.get("rows", [])
        actual_rows = action_response.get("rows", [])

        passed, description = contains_rows(expected_rows, actual_rows)

        return AssertResult(
            passed=passed,
            expected=str(expected_rows),
            actual=str(actual_rows),
            description=description,
        )
    elif assert_type == "EqualsRows":
        expected_rows = expected.get("rows", [])
        actual_rows = action_response.get("rows", [])

        passed, description = equals_rows(expected_rows, actual_rows)

        return AssertResult(
            passed=passed,
            expected=str(expected_rows),
            actual=str(actual_rows),
            description=description,
        )
    else:
        raise ValueError(f"Assert type {assert_type} is invalid")
