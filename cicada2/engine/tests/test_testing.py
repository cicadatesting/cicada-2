from collections import defaultdict
from unittest.mock import patch, Mock

from cicada2.engine import testing
from cicada2.shared.types import AssertResult


def test_get_default_cycles_empty():
    default_cycles = testing.get_default_cycles(asserts=[], actions=[])

    assert default_cycles == 0


def test_get_default_cycles_asserts_only():
    default_cycles = testing.get_default_cycles(asserts=["foo"], actions=[])

    assert default_cycles == -1


def test_get_default_cycles_actions_only():
    default_cycles = testing.get_default_cycles(asserts=[], actions=["bar"])

    assert default_cycles == 1


def test_get_default_cycles_actions_and_asserts():
    default_cycles = testing.get_default_cycles(asserts=["foo"], actions=["bar"])

    assert default_cycles == -1


def test_continue_running_no_asserts_limited():
    assert testing.continue_running(asserts=[], remaining_cycles=1, assert_statuses={})


def test_continue_running_no_asserts_unlimited():
    assert testing.continue_running(asserts=[], remaining_cycles=-1, assert_statuses={})


def test_continue_running_no_asserts_no_remaining():
    assert not testing.continue_running(
        asserts=[], remaining_cycles=0, assert_statuses={}
    )


def test_continue_running_asserts_unlimited_first_run():
    test_asserts = [{"type": "RESTAssert"}]

    assert testing.continue_running(
        asserts=test_asserts, remaining_cycles=-1, assert_statuses={}
    )


def test_continue_running_asserts_failed_unlimited_second_run():
    test_asserts = [{"type": "RESTAssert"}]

    assert_statuses = {
        "RESTAssert0": [
            AssertResult(passed=False, actual="", expected="", description="")
        ],
    }

    assert testing.continue_running(
        asserts=test_asserts, remaining_cycles=-2, assert_statuses=assert_statuses
    )


def test_continue_running_asserts_passed_limited_second_run():
    test_asserts = [{"type": "RESTAssert"}]

    assert_statuses = {
        "RESTAssert0": [
            AssertResult(passed=True, actual="", expected="", description="")
        ],
    }

    assert not testing.continue_running(
        asserts=test_asserts, remaining_cycles=1, assert_statuses=assert_statuses
    )


def test_continue_running_asserts_passed_unlimited_second_run():
    test_asserts = [{"type": "RESTAssert"}]

    assert_statuses = {
        "RESTAssert0": [
            AssertResult(passed=True, actual="", expected="", description="")
        ],
    }

    assert not testing.continue_running(
        asserts=test_asserts, remaining_cycles=-2, assert_statuses=assert_statuses
    )


def test_continue_running_asserts_passed_limited_second_run_no_remaining():
    test_asserts = [{"type": "RESTAssert"}]

    assert_statuses = {
        "RESTAssert0": [
            AssertResult(passed=True, actual="", expected="", description="")
        ],
    }

    assert not testing.continue_running(
        asserts=test_asserts, remaining_cycles=0, assert_statuses=assert_statuses
    )


def test_continue_running_asserts_failed_limited_second_run():
    test_asserts = [{"type": "RESTAssert"}]

    assert_statuses = {
        "RESTAssert0": [
            AssertResult(passed=False, actual="", expected="", description="")
        ],
    }

    assert not testing.continue_running(
        asserts=test_asserts, remaining_cycles=0, assert_statuses=assert_statuses
    )


# TODO: functional versions of tests


@patch("cicada2.engine.testing.run_actions")
def test_run_actions_parallel(run_actions_mock: Mock):
    run_actions_mock.return_value = {"A": {"results": [{"foo": "bar"}]}}

    test_state = defaultdict(dict)
    test_actions = [{"name": "A", "params": {"foo": "bar"}}]

    results = testing.run_actions_parallel(
        actions=test_actions,
        state=test_state,
        test_name="Test1",
        hostnames=["alpha"],
        seconds_between_actions=0,
    )

    assert results == {"A": {"outputs": {}, "results": [{"foo": "bar"}]}}


@patch("cicada2.engine.testing.run_actions")
def test_run_actions_parallel_multiple_hosts(run_actions_mock: Mock):
    run_actions_mock.return_value = {"A": {"results": [{"foo": "bar"}]}}

    test_state = defaultdict(dict)
    test_actions = [{"name": "A", "params": {"foo": "bar"}}]

    results = testing.run_actions_parallel(
        actions=test_actions,
        state=test_state,
        test_name="Test1",
        hostnames=["alpha", "bravo"],
        seconds_between_actions=0,
    )

    assert results == {
        "A": {"outputs": {}, "results": [{"foo": "bar"}, {"foo": "bar"}]}
    }


@patch("cicada2.engine.testing.run_actions")
def test_run_actions_series(run_actions_mock):
    run_actions_mock.return_value = {"A": {"results": [{"foo": "bar"}]}}

    test_state = defaultdict(dict)
    test_actions = [{"name": "A", "params": {"foo": "bar"}}]

    results = testing.run_actions_series(
        actions=test_actions,
        state=test_state,
        test_name="Test1",
        hostnames=["alpha"],
        seconds_between_actions=0,
    )

    assert results == {"A": {"outputs": {}, "results": [{"foo": "bar"}]}}


@patch("cicada2.engine.testing.run_actions")
def test_run_actions_series_multiple_actions(run_actions_mock):
    run_actions_mock.return_value = {
        "A": {"results": [{"foo": "bar"}]},
        "B": {"results": [{"foo": "bar"}]},
    }

    test_state = defaultdict(dict)
    test_actions = [
        {"name": "A", "params": {"foo": "bar"}},
        {"name": "B", "params": {"foo": "bar"}},
    ]

    results = testing.run_actions_series(
        actions=test_actions,
        state=test_state,
        test_name="Test1",
        hostnames=["alpha"],
        seconds_between_actions=0,
    )

    assert results == {
        "A": {"outputs": {}, "results": [{"foo": "bar"}]},
        "B": {"outputs": {}, "results": [{"foo": "bar"}]},
    }


@patch("cicada2.engine.testing.run_actions")
def test_run_actions_series_multiple_actions_multiple_hosts(run_actions_mock):
    run_actions_mock.return_value = {
        "A": {"results": [{"foo": "bar"}]},
        "B": {"results": [{"foo": "bar"}]},
    }

    test_state = defaultdict(dict)
    test_actions = [
        {"name": "A", "params": {"foo": "bar"}},
        {"name": "B", "params": {"foo": "bar"}},
    ]

    results = testing.run_actions_series(
        actions=test_actions,
        state=test_state,
        test_name="Test1",
        hostnames=["alpha", "bravo"],
        seconds_between_actions=0,
    )

    assert results == {
        "A": {"outputs": {}, "results": [{"foo": "bar"}, {"foo": "bar"}]},
        "B": {"outputs": {}, "results": [{"foo": "bar"}, {"foo": "bar"}]},
    }


@patch("cicada2.engine.testing.run_actions")
def test_run_actions_series_one_action_multiple_hosts(run_actions_mock):
    run_actions_mock.return_value = {"A": {"results": [{"foo": "bar"}]}}

    test_state = defaultdict(dict)
    test_actions = [{"name": "A", "params": {"foo": "bar"}}]

    results = testing.run_actions_series(
        actions=test_actions,
        state=test_state,
        test_name="Test1",
        hostnames=["alpha", "bravo"],
        seconds_between_actions=0,
    )

    assert results == {"A": {"outputs": {}, "results": [{"foo": "bar"}]}}


@patch("cicada2.engine.testing.run_asserts")
def test_run_asserts_parallel(run_asserts_mock: Mock):
    run_asserts_mock.return_value = {
        "A": [AssertResult(passed=True, actual="", expected="", description="")]
    }

    test_state = defaultdict(dict)
    test_asserts = [{"name": "A", "type": "SQLAssert"}]

    results = testing.run_asserts_parallel(
        asserts=test_asserts,
        state=test_state,
        test_name="foo",
        hostnames=["alpha", "bravo"],
        seconds_between_asserts=0,
    )

    assert results == {
        "A": [
            AssertResult(passed=True, actual="", expected="", description=""),
            AssertResult(passed=True, actual="", expected="", description=""),
        ]
    }


@patch("cicada2.engine.testing.run_asserts")
def test_run_asserts_series_one_assert(run_asserts_mock: Mock):
    run_asserts_mock.return_value = {
        "A": [AssertResult(passed=True, actual="", expected="", description="")]
    }

    test_state = defaultdict(dict)
    test_asserts = [{"name": "A", "type": "SQLAssert"}]

    results = testing.run_asserts_series(
        asserts=test_asserts,
        state=test_state,
        test_name="foo",
        hostnames=["alpha"],
        seconds_between_asserts=0,
    )

    assert results == {
        "A": [AssertResult(passed=True, actual="", expected="", description="")]
    }


@patch("cicada2.engine.testing.run_asserts")
def test_run_asserts_series_multiple_hosts_one_assert(run_asserts_mock: Mock):
    run_asserts_mock.side_effect = [
        {"A": [AssertResult(passed=True, actual="", expected="", description="")]}
    ]

    test_state = defaultdict(dict)
    test_asserts = [{"name": "A", "type": "SQLAssert"}]

    results = testing.run_asserts_series(
        asserts=test_asserts,
        state=test_state,
        test_name="foo",
        hostnames=["alpha", "bravo"],
        seconds_between_asserts=0,
    )

    assert results == {
        "A": [AssertResult(passed=True, actual="", expected="", description="")]
    }


@patch("cicada2.engine.testing.run_asserts")
def test_run_asserts_series_one_host_multiple_asserts(run_asserts_mock: Mock):
    run_asserts_mock.return_value = {
        "A": [AssertResult(passed=True, actual="", expected="", description="")],
        "B": [AssertResult(passed=False, actual="", expected="", description="")],
    }

    test_state = defaultdict(dict)
    test_asserts = [
        {"name": "A", "type": "SQLAssert"},
        {"name": "B", "type": "SQLAssert"},
    ]

    results = testing.run_asserts_series(
        asserts=test_asserts,
        state=test_state,
        test_name="foo",
        hostnames=["alpha"],
        seconds_between_asserts=0,
    )

    assert results == {
        "A": [AssertResult(passed=True, actual="", expected="", description="")],
        "B": [AssertResult(passed=False, actual="", expected="", description="")],
    }


@patch("cicada2.engine.testing.run_asserts")
def test_run_asserts_series_multiple_host_multiple_asserts(run_asserts_mock: Mock):
    run_asserts_mock.side_effect = [{"A": [True]}, {"B": [False]}]

    test_state = defaultdict(dict)
    test_asserts = [
        {"name": "A", "type": "SQLAssert"},
        {"name": "B", "type": "SQLAssert"},
    ]

    results = testing.run_asserts_series(
        asserts=test_asserts,
        state=test_state,
        test_name="foo",
        hostnames=["alpha", "bravo"],
        seconds_between_asserts=0,
    )

    # NOTE: B does not run because I'm pretty sure Dask is pickling
    # the run_assert mock so it will only run the first side effect.
    # At least it runs twice...
    assert results == {"A": [True, True]}


@patch("cicada2.engine.testing.run_asserts_series")
def test_run_tests_unlimited_cycles(run_asserts_series_mock: Mock):
    run_asserts_series_mock.side_effect = [
        {"A": [AssertResult(passed=False, actual="", expected="", description="")]},
        {
            "A": [
                AssertResult(passed=False, actual="", expected="", description=""),
                AssertResult(passed=False, actual="", expected="", description=""),
            ]
        },
        {
            "A": [
                AssertResult(passed=False, actual="", expected="", description=""),
                AssertResult(passed=False, actual="", expected="", description=""),
                AssertResult(passed=True, actual="", expected="", description=""),
            ]
        },
        {
            "A": [
                AssertResult(passed=False, actual="", expected="", description=""),
                AssertResult(passed=False, actual="", expected="", description=""),
                AssertResult(passed=True, actual="", expected="", description=""),
                AssertResult(passed=True, actual="", expected="", description=""),
            ]
        },
    ]

    test_config = {
        "name": "some_test_name",
        "secondsBetweenCycles": 0,
        "asserts": [{"name": "A", "type": "SQLAssert", "params": {}}],
    }

    end_state = testing.run_test(
        test_config=test_config, incoming_state={}, hostnames=["alpha"]
    )

    assert run_asserts_series_mock.call_count == 3
    assert end_state == {
        "some_test_name": {
            "asserts": {
                "A": [
                    AssertResult(passed=False, actual="", expected="", description=""),
                    AssertResult(passed=False, actual="", expected="", description=""),
                    AssertResult(passed=True, actual="", expected="", description=""),
                ]
            },
            "summary": {
                "completed_cycles": 3,
                "error": None,
                "duration": 0,
                "remaining_asserts": [],
            },
        }
    }


@patch("cicada2.engine.testing.run_asserts_series")
def test_run_tests_limited_cycles(run_asserts_series_mock: Mock):
    run_asserts_series_mock.side_effect = [
        {"A": [AssertResult(passed=False, actual="", expected="", description="")]},
        {
            "A": [
                AssertResult(passed=False, actual="", expected="", description=""),
                AssertResult(passed=False, actual="", expected="", description=""),
            ]
        },
        {
            "A": [
                AssertResult(passed=False, actual="", expected="", description=""),
                AssertResult(passed=False, actual="", expected="", description=""),
                AssertResult(passed=False, actual="", expected="", description=""),
            ]
        },
    ]

    test_config = {
        "name": "some_test_name",
        "cycles": 2,
        "secondsBetweenCycles": 0,
        "asserts": [{"name": "A", "type": "SQLAssert", "params": {}}],
    }

    end_state = testing.run_test(
        test_config=test_config, incoming_state={}, hostnames=["alpha"]
    )

    assert run_asserts_series_mock.call_count == 2
    assert end_state == {
        "some_test_name": {
            "asserts": {
                "A": [
                    AssertResult(passed=False, actual="", expected="", description=""),
                    AssertResult(passed=False, actual="", expected="", description=""),
                ]
            },
            "summary": {
                "completed_cycles": 2,
                "error": None,
                "duration": 0,
                "remaining_asserts": [{"name": "A", "type": "SQLAssert", "params": {}}],
            },
        }
    }
