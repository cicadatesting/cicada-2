from unittest.mock import patch

from cicada2.engine import actions


@patch("cicada2.engine.actions.get_action_sender")
def test_run_actions(get_action_sender_mock):
    get_action_sender_mock.return_value.__enter__.return_value.return_value = {
        "foo": "bar"
    }

    test_actions = [
        {
            "type": "POST",
            "name": "POST0",
            "executionsPerCycle": 2,
            "params": {"foo": "bar"},
            "outputs": [{"name": "A", "value": "xyz"}],
        },
        {"name": "X", "params": {"fizz": "buzz"}},
    ]

    actions_data = actions.run_actions(test_actions, {}, "", 0)

    assert actions_data["POST0"]["results"] == [{"foo": "bar"}, {"foo": "bar"}]
    assert actions_data["POST0"]["outputs"]["A"] == "xyz"
    assert actions_data["X"]["results"] == [{"foo": "bar"}]


@patch("cicada2.engine.actions.get_action_sender")
def test_run_actions_with_asserts(get_action_sender_mock):
    get_action_sender_mock.return_value.__enter__.return_value.return_value = {
        "foo": "bar",
        "fizz": "buzz",
    }

    test_actions = [
        {
            "type": "POST",
            "name": "POST0",
            "params": {"foo": "bar"},
            "asserts": [{"name": "Assert0", "expected": {"foo": "bar"}}],
        }
    ]

    actions_data = actions.run_actions(test_actions, {}, "", 0)

    assert actions_data["POST0"]["results"] == [{"foo": "bar", "fizz": "buzz"}]
    assert actions_data["POST0"]["asserts"]["Assert0"][0]["passed"]


@patch("cicada2.engine.actions.get_action_sender")
def test_run_actions_with_asserts_actual_override(get_action_sender_mock):
    get_action_sender_mock.return_value.__enter__.return_value.return_value = {
        "foo": ["fizz", "buzz"]
    }

    test_actions = [
        {
            "type": "POST",
            "name": "POST0",
            "params": {"foo": "bar"},
            "asserts": [
                {
                    "name": "Assert0",
                    "expected": 2,
                    "template": """
                        actual: {{ result['foo']|length }}
                    """,
                }
            ],
        }
    ]

    actions_data = actions.run_actions(test_actions, {}, "", 0)

    assert actions_data["POST0"]["asserts"]["Assert0"][0]["passed"]


@patch("cicada2.engine.actions.get_action_sender")
def test_run_actions_with_asserts_multiple_calls_versioned(
    get_action_sender_mock,
):
    get_action_sender_mock.return_value.__enter__.return_value.side_effect = [
        {"foo": "bar"},
        {"fizz": "buzz"},
    ]

    test_actions = [
        {
            "type": "POST",
            "name": "POST0",
            "params": {"foo": "bar"},
            "executionsPerCycle": 2,
            "asserts": [
                {
                    "name": "Assert0",
                    "expected": {"foo": "bar"},
                    "storeVersions": True,
                },
                {
                    "name": "Assert1",
                    "expected": {"fizz": "buzz"},
                    "storeVersions": True,
                },
            ],
        }
    ]

    actions_data = actions.run_actions(test_actions, {}, "", 0)

    assert actions_data["POST0"]["results"] == [{"foo": "bar"}, {"fizz": "buzz"}]

    # Assert0 passed
    # Assert1 fails, then passed
    assert actions_data["POST0"]["asserts"]["Assert0"][0]["passed"]
    assert not actions_data["POST0"]["asserts"]["Assert1"][0]["passed"]
    assert actions_data["POST0"]["asserts"]["Assert1"][1]["passed"]


@patch("cicada2.engine.actions.get_action_sender")
def test_run_actions_with_asserts_multiple_calls_versioned_keep_if_passed(
    get_action_sender_mock,
):
    get_action_sender_mock.return_value.__enter__.return_value.side_effect = [
        {"foo": "bar"},
        {"fizz": "buzz"},
    ]

    test_actions = [
        {
            "type": "POST",
            "name": "POST0",
            "params": {"foo": "bar"},
            "executionsPerCycle": 2,
            "asserts": [
                {
                    "name": "Assert0",
                    "expected": {"foo": "bar"},
                    "storeVersions": True,
                    "keepIfPassed": True,
                },
                {
                    "name": "Assert1",
                    "expected": {"fizz": "buzz"},
                    "storeVersions": True,
                    "keepIfPassed": True,
                },
            ],
        }
    ]

    actions_data = actions.run_actions(test_actions, {}, "", 0)

    assert actions_data["POST0"]["results"] == [{"foo": "bar"}, {"fizz": "buzz"}]

    # Assert0 passed, then fails
    # Assert1 fails, then passed
    assert actions_data["POST0"]["asserts"]["Assert0"][0]["passed"]
    assert actions_data["POST0"]["asserts"]["Assert1"][1]["passed"]

    assert not actions_data["POST0"]["asserts"]["Assert0"][1]["passed"]
    assert not actions_data["POST0"]["asserts"]["Assert1"][0]["passed"]


@patch("cicada2.engine.actions.get_action_sender")
def test_run_actions_errored_call(get_action_sender_mock):
    get_action_sender_mock.return_value.__enter__.return_value.side_effect = [
        {"foo": "bar"},
        {},
        {},
    ]

    test_actions = [
        {
            "type": "POST",
            "name": "POST0",
            "executionsPerCycle": 2,
            "params": {"foo": "bar"},
            "outputs": [{"name": "A", "value": "xyz"}],
        },
        {"name": "X", "params": {"fizz": "buzz"}},
    ]

    actions_data = actions.run_actions(test_actions, {}, "", 0)

    assert actions_data["POST0"]["results"] == [{"foo": "bar"}, {}]
    assert actions_data["POST0"]["outputs"]["A"] == "xyz"
    assert actions_data["X"]["results"] == [{}]


@patch("cicada2.engine.actions.get_action_sender")
def test_run_actions_non_versioned(get_action_sender_mock):
    get_action_sender_mock.return_value.__enter__.return_value.return_value = {
        "foo": "bar"
    }

    test_actions = [
        {
            "type": "POST",
            "name": "POST0",
            "executionsPerCycle": 2,
            "storeVersions": False,
            "params": {"foo": "bar"},
            "outputs": [{"name": "A", "value": "xyz", "storeVersions": True}],
        },
        {"name": "X", "params": {"fizz": "buzz"}},
    ]

    actions_data = actions.run_actions(test_actions, {}, "", 0)

    assert actions_data["POST0"]["results"] == {"foo": "bar"}
    assert actions_data["POST0"]["outputs"]["A"] == ["xyz"]
    assert actions_data["X"]["results"] == [{"foo": "bar"}]


def test_run_assert_from_action_result_negated():
    asrt = {"name": "foo", "expected": {"fizz", "buzz"}, "negate": True}
    action_result = {"foo", "bar"}

    assert_result = actions.run_assert_from_action_result(asrt, action_result)

    assert assert_result["passed"]


def test_run_assert_from_action_result_negated_passed():
    asrt = {"name": "foo", "expected": {"fizz", "buzz"}, "negate": True}
    action_result = {"fizz", "buzz"}

    assert_result = actions.run_assert_from_action_result(asrt, action_result)

    assert not assert_result["passed"]


def test_combine_action_data():
    current_actions_data = {
        "POST0": {
            "results": [{"foo": "bar"}, {"foo": "bar"}],
            "outputs": {"A": ["xyz"]},
            "asserts": {"Assert0": {"passed": False}, "Assert1": [{"passed": False}]},
        }
    }

    new_actions_data = {
        "POST0": {
            "results": [{"foo": "bar"}, {"foo": "bar"}],
            "outputs": {"A": ["xyz"]},
            "asserts": {"Assert0": {"passed": True}, "Assert1": [{"passed": True}]},
        },
        "X": {"results": [{"foo": "bar"}]},
    }

    combined_actions_data = actions.combine_action_data(
        current_actions_data, new_actions_data
    )

    assert combined_actions_data["POST0"]["results"] == [
        {"foo": "bar"},
        {"foo": "bar"},
        {"foo": "bar"},
        {"foo": "bar"},
    ]

    assert combined_actions_data["POST0"]["outputs"]["A"] == ["xyz", "xyz"]
    assert combined_actions_data["X"]["results"] == [{"foo": "bar"}]
    assert combined_actions_data["POST0"]["asserts"]["Assert0"]["passed"]
    assert combined_actions_data["POST0"]["asserts"]["Assert1"] == [
        {"passed": False},
        {"passed": True},
    ]


def test_combine_action_data_error():
    current_actions_data = {
        "POST0": {
            "results": [{"foo": "bar"}, {"foo": "bar"}],
            "outputs": {"A": ["xyz"]},
        }
    }

    new_actions_data = {
        "POST0": {"results": [{}, {}], "outputs": {"A": ["xyz"]}},
        "X": {"results": [{"foo": "bar"}]},
    }

    combined_actions_data = actions.combine_action_data(
        current_actions_data, new_actions_data
    )

    assert combined_actions_data["POST0"]["results"] == [
        {"foo": "bar"},
        {"foo": "bar"},
        {},
        {},
    ]

    assert combined_actions_data["POST0"]["outputs"]["A"] == ["xyz", "xyz"]
    assert combined_actions_data["X"]["results"] == [{"foo": "bar"}]
