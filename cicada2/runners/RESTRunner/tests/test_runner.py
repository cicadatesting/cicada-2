import json
from unittest.mock import Mock

from requests.auth import HTTPBasicAuth

from cicada2.runners.RESTRunner import runner


def test_parse_action_params_auth():
    params = {
        'url': 'xyz.com',
        'username': 'foo',
        'password': 'bar'
    }

    parsed_params = runner.parse_action_params(params)

    assert parsed_params['auth'] == HTTPBasicAuth(
        username='foo',
        password='bar'
    )


def test_parse_action_params_auth_missing():
    params = {
        'url': 'xyz.com',
        'username': 'foo'
    }

    parsed_params = runner.parse_action_params(params)

    assert parsed_params['auth'] is None


def test_parse_response_body_successful():
    response_body = {
        'foo': 'bar'
    }

    response = Mock()
    response.text = json.dumps(response_body)
    response.json.return_value = response_body

    text, body = runner.parse_response_body(response)

    assert text == json.dumps(body)
    assert body == response_body


def test_action_params_problems_successful():
    params = {
        'url': 'xyz.com'
    }

    problems = runner.action_params_problems(params=params)

    assert problems == []


def test_action_params_problems_no_url():
    problems = runner.action_params_problems(params={})

    assert problems == ['Missing "url" in action params']


def test_assert_dicts_passed_all_required():
    test_dict = {
        'foo': 'bar'
    }

    passed, description = runner.assert_dicts(
        expected=test_dict,
        actual=test_dict,
        all_required=True
    )

    assert passed
    assert description == 'passed'


def test_assert_dicts_failed_all_required():
    expected_dict = {
        'foo': 'bar'
    }

    actual_dict = {
        'foo': 'bar',
        'fizz': 'buzz'
    }

    passed, description = runner.assert_dicts(
        expected=expected_dict,
        actual=actual_dict,
        all_required=True
    )

    assert not passed
    assert description == "Expected {'foo': 'bar'}, got {'foo': 'bar', 'fizz': 'buzz'}"


def test_assert_dicts_passed_subset():
    expected_dict = {
        'foo': 'bar'
    }

    actual_dict = {
        'foo': 'bar',
        'fizz': 'buzz'
    }

    passed, description = runner.assert_dicts(
        expected=expected_dict,
        actual=actual_dict,
        all_required=False
    )

    assert passed
    assert description == 'passed'


def test_assert_dicts_failed_subset():
    expected_dict = {
        'foo': 'bar'
    }

    actual_dict = {
        'fizz': 'buzz'
    }

    passed, description = runner.assert_dicts(
        expected=expected_dict,
        actual=actual_dict,
        all_required=False
    )

    assert not passed
    assert description == "Expected {'foo': 'bar'} to be in {'fizz': 'buzz'}"


def test_assert_params_problems_no_url():
    assert_params = {
        'method': 'GET',
        'expected': 200,
        'actionParams': {
            'headers': {
                'foo': 'bar'
            }
        }
    }

    problems = runner.assert_params_problems(assert_params)

    assert problems == ['Missing "url" in action params']


def test_assert_params_problems_no_action_params():
    assert_params = {
        'method': 'GET',
        'expected': 200
    }

    problems = runner.assert_params_problems(assert_params)

    assert problems == ["Missing 'actionParams' in assert params", 'Missing "url" in action params']
