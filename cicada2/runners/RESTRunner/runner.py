from json import JSONDecodeError
from datetime import datetime
from typing import Dict, List, Optional, Tuple, NamedTuple, Union
from typing_extensions import TypedDict

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import BaseHTTPError

from cicada2.runners.util.asserts import assert_dicts
from cicada2.runners.util.types import AssertResult


class ActionParams(TypedDict):
    url: str
    headers: Optional[Dict[str, str]]
    queryParams: Optional[Dict[str, str]]
    body: Optional[dict]
    username: Optional[str]
    password: Optional[str]


class RequestParams(TypedDict):
    url: str
    headers: Optional[Dict[str, str]]
    params: Optional[Dict[str, str]]
    json: Optional[dict]
    auth: HTTPBasicAuth


class ActionResponse(TypedDict):
    status_code: int
    headers: Dict[str, str]
    body: dict
    text: str
    runtime: int


class AssertParams(TypedDict):
    actionParams: ActionParams
    method: str
    expected: Union[int, dict]
    allRequired: Optional[bool]


def parse_action_params(params: ActionParams) -> RequestParams:
    url = params['url']
    headers = params.get('headers')
    query_params = params.get('queryParams')
    body = params.get('body')
    username = params.get('username')
    password = params.get('password')

    if username and password:
        auth = HTTPBasicAuth(username, password)
    else:
        auth = None
    # TODO: support for oauth

    return {
        'url': url,
        'headers': headers,
        'json': body,
        'params': query_params,
        'auth': auth
    }


def parse_response_body(response: requests.Response) -> Tuple[str, dict]:
    try:
        return response.text, response.json()
    except JSONDecodeError:
        # Cannot load JSON from text
        return response.text, {}
    except AttributeError:
        # Response text is empty
        return '', {}


def action_params_problems(params: ActionParams) -> List[str]:
    problems = []

    if 'url' not in params:
        problems.append('Missing "url" in action params')

    return problems


def run_action(action_type: str, params: ActionParams) -> ActionResponse:
    params_problems = action_params_problems(params)

    if params_problems:
        raise ValueError(f"Params invalid: {', '.join(params_problems)}")

    request_params = parse_action_params(params)

    # NOTE: support for cookies?
    # NOTE: support for cert file?
    # NOTE: support for digest auth?
    # NOTE: support for generic methods?

    # TODO: unit test for errors raised

    try:
        if action_type in ['GET', 'DELETE', 'POST', 'PATCH', 'PUT']:
            start = datetime.now()
            response = requests.request(method=action_type, **request_params)
            end = datetime.now()
        else:
            raise ValueError(f"Action type {action_type} is invalid")
    except BaseHTTPError as e:
        raise RuntimeError(f"Request failed: {e}")

    text, body = parse_response_body(response)

    return {
        'status_code': response.status_code,
        'headers': dict(response.headers),
        'body': body,
        'text': text,
        'runtime': (end - start).microseconds / 1000
    }


def assert_params_problems(params: AssertParams) -> List[str]:
    problems = []

    if 'method' not in params:
        problems.append("Missing 'method' in assert params")

    if 'actionParams' not in params:
        problems.append("Missing 'actionParams' in assert params")

    if 'expected' not in params:
        problems.append("Missing 'expected' in assert params")

    problems.extend(
        action_params_problems(
            params.get('actionParams', {})
        )
    )

    return problems


def run_assert(assert_type: str, params: AssertParams) -> AssertResult:
    params_problems = assert_params_problems(params)

    if params_problems:
        raise ValueError(f"Params invalid: {', '.join(params_problems)}")

    action_response = run_action(params['method'], params['actionParams'])
    expected = params['expected']

    if assert_type == 'Headers':
        actual = action_response['headers']

        passed, description = assert_dicts(
            expected=expected,
            actual=actual,
            all_required=params.get('allRequired', False)
        )
    elif assert_type == 'JSON':
        actual = action_response['body']

        passed, description = assert_dicts(
            expected=expected,
            actual=actual,
            all_required=params.get('allRequired', False)
        )
    elif assert_type == 'StatusCode':
        actual = action_response['status_code']

        passed = expected == actual

        if not passed:
            description = f"expected status code {expected}, got {actual}"
        else:
            description = 'passed'
    else:
        raise ValueError(f"Assert type {assert_type} is invalid")

    return AssertResult(
        passed=passed,
        expected=str(expected),
        actual=str(actual),
        description=description
    )
