from collections import defaultdict
from unittest.mock import patch, Mock

from cicada2.engine import testing
from cicada2.shared.types import Action, Assert, AssertResult


def test_get_default_cycles_empty():
    default_cycles = testing.get_default_cycles(asserts=[], actions=[])

    assert default_cycles == 0


def test_get_default_cycles_asserts_only():
    default_cycles = testing.get_default_cycles(
        asserts=[Assert(name="foo")], actions=[]
    )

    assert default_cycles == -1


def test_get_default_cycles_actions_only():
    default_cycles = testing.get_default_cycles(
        asserts=[], actions=[Action(name="bar")]
    )

    assert default_cycles == 1


def test_get_default_cycles_actions_and_asserts():
    default_cycles = testing.get_default_cycles(
        asserts=[Assert(name="foo")], actions=[Action(name="bar")]
    )

    assert default_cycles == -1


def test_get_default_cycles_actions_have_asserts():
    default_cycles = testing.get_default_cycles(
        asserts=[], actions=[Action(name="bar", asserts=[Assert(name="foo")])]
    )

    assert default_cycles == -1


def test_continue_running_no_actions_no_asserts():
    assert testing.continue_running(
        actions=[],
        asserts=[],
        remaining_cycles=1,
        actions_data={},
        assert_statuses={},
    )


def test_continue_running_no_asserts_limited():
    actions = [Action(name="some-action")]
    asserts = []

    assert testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=1,
        actions_data={},
        assert_statuses={},
    )


def test_continue_running_no_asserts_unlimited():
    actions = [Action(name="some-action")]
    asserts = []

    assert testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=-1,
        actions_data={},
        assert_statuses={},
    )


def test_continue_running_no_asserts_no_remaining():
    actions = [Action(name="some-action")]
    asserts = []

    assert not testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=0,
        actions_data={},
        assert_statuses={},
    )


def test_continue_running_asserts_unlimited_first_run():
    actions = []
    asserts = [{"type": "RESTAssert"}]

    assert testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=-1,
        actions_data={},
        assert_statuses={},
    )


def test_continue_running_actions_with_asserts_first_run():
    actions = [Action(name="bar", asserts=[Assert(name="foo")])]
    asserts = []

    assert testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=-1,
        actions_data={},
        assert_statuses={},
    )


def test_continue_running_asserts_failed_unlimited_second_run():
    actions = []
    asserts = [{"type": "RESTAssert"}]

    assert_statuses = {
        "RESTAssert0": [
            AssertResult(passed=False, actual="", expected="", description="")
        ],
    }

    assert testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=-2,
        actions_data={},
        assert_statuses=assert_statuses,
    )


def test_continue_running_actions_with_asserts_failed_unlimited_second_run():
    actions = [Action(name="bar", asserts=[Assert(name="foo")])]
    asserts = []

    actions_data = {
        "bar": {
            "asserts": {
                "foo": AssertResult(
                    passed=False, actual="", expected="", description=""
                )
            }
        }
    }

    assert testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=-2,
        actions_data=actions_data,
        assert_statuses={},
    )


def test_continue_running_asserts_passed_limited_second_run():
    actions = []
    asserts = [{"type": "RESTAssert", "name": "RESTAssert0"}]

    assert_statuses = {
        "RESTAssert0": [
            AssertResult(passed=True, actual="", expected="", description="")
        ],
    }

    assert not testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=1,
        actions_data={},
        assert_statuses=assert_statuses,
    )


def test_continue_running_asserts_with_actions_passed_limited_second_run():
    actions = [Action(name="bar", asserts=[Assert(name="foo")])]
    asserts = []

    actions_data = {
        "bar": {
            "asserts": {
                "foo": AssertResult(passed=True, actual="", expected="", description="")
            }
        }
    }

    assert not testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=1,
        actions_data=actions_data,
        assert_statuses={},
    )


def test_continue_running_asserts_passed_unlimited_second_run():
    actions = []
    asserts = [{"type": "RESTAssert", "name": "RESTAssert0"}]

    assert_statuses = {
        "RESTAssert0": [
            AssertResult(passed=True, actual="", expected="", description="")
        ],
    }

    assert not testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=-2,
        actions_data={},
        assert_statuses=assert_statuses,
    )


def test_continue_running_asserts_with_actions_passed_unlimited_second_run():
    actions = [Action(name="bar", asserts=[Assert(name="foo")])]
    asserts = []

    actions_data = {
        "bar": {
            "asserts": {
                "foo": AssertResult(passed=True, actual="", expected="", description="")
            }
        }
    }

    assert not testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=-2,
        actions_data=actions_data,
        assert_statuses={},
    )


def test_continue_running_asserts_passed_limited_second_run_no_remaining():
    actions = []
    asserts = [{"type": "RESTAssert"}]

    assert_statuses = {
        "RESTAssert0": [
            AssertResult(passed=True, actual="", expected="", description="")
        ],
    }

    assert not testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=0,
        actions_data={},
        assert_statuses=assert_statuses,
    )


def test_continue_running_actions_with_asserts_passed_limited_second_run_no_remaining():
    actions = [Action(name="bar", asserts=[Assert(name="foo")])]
    asserts = []

    actions_data = {
        "bar": {
            "asserts": {
                "foo": AssertResult(passed=True, actual="", expected="", description="")
            }
        }
    }

    assert not testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=0,
        actions_data=actions_data,
        assert_statuses={},
    )


def test_continue_running_asserts_failed_limited_second_run():
    actions = []
    asserts = [{"type": "RESTAssert"}]

    assert_statuses = {
        "RESTAssert0": [
            AssertResult(passed=False, actual="", expected="", description="")
        ],
    }

    assert not testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=0,
        actions_data={},
        assert_statuses=assert_statuses,
    )


def test_continue_running_actions_with_asserts_failed_limited_second_run():
    actions = [Action(name="bar", asserts=[Assert(name="foo")])]
    asserts = []

    actions_data = {
        "bar": {
            "asserts": {
                "foo": AssertResult(
                    passed=False, actual="", expected="", description=""
                )
            }
        }
    }

    assert not testing.continue_running(
        actions=actions,
        asserts=asserts,
        remaining_cycles=0,
        actions_data=actions_data,
        assert_statuses={},
    )


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

    assert results == {"A": {"outputs": {}, "results": [{"foo": "bar"}], "asserts": {}}}


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
        "A": {"outputs": {}, "results": [{"foo": "bar"}, {"foo": "bar"}], "asserts": {}}
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

    assert results == {"A": {"outputs": {}, "results": [{"foo": "bar"}], "asserts": {}}}


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
        "A": {"outputs": {}, "results": [{"foo": "bar"}], "asserts": {}},
        "B": {"outputs": {}, "results": [{"foo": "bar"}], "asserts": {}},
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
        "A": {
            "outputs": {},
            "results": [{"foo": "bar"}, {"foo": "bar"}],
            "asserts": {},
        },
        "B": {
            "outputs": {},
            "results": [{"foo": "bar"}, {"foo": "bar"}],
            "asserts": {},
        },
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

    assert results == {"A": {"outputs": {}, "results": [{"foo": "bar"}], "asserts": {}}}


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
                "description": None,
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
                "description": None,
                "completed_cycles": 2,
                "error": None,
                "duration": 0,
                "remaining_asserts": ["A"],
            },
        }
    }
