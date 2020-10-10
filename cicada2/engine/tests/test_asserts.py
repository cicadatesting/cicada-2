from unittest.mock import patch

from cicada2.engine import asserts
from cicada2.shared.types import AssertResult


@patch("cicada2.engine.asserts.send_assert")
def test_run_asserts(mock_send_assert):
    mock_send_assert.return_value = AssertResult(
        passed=True, actual="foo", expected="foo", description="good"
    )

    test_asserts = [
        {"name": "A", "type": "SQLAssert", "params": {}, "executionsPerCycle": 2},
        {"name": "B", "type": "NullAssert", "passed": True, "params": {}},
        {"name": "C", "type": "NullAssert", "params": {}},
    ]

    statuses = asserts.run_asserts(test_asserts, {}, "", 0)

    assert statuses["A"] == [
        AssertResult(passed=True, actual="foo", expected="foo", description="good"),
        AssertResult(passed=True, actual="foo", expected="foo", description="good"),
    ]

    assert statuses["B"] == [
        AssertResult(passed=True, actual="", expected="", description="")
    ]

    assert statuses["C"] == [
        AssertResult(passed=False, actual="", expected="", description="")
    ]


# TODO: test remote assert errors


@patch("cicada2.engine.asserts.send_assert")
def test_asserts_non_versioned(mock_send_assert):
    mock_send_assert.return_value = AssertResult(
        passed=True, actual="foo", expected="foo", description="good"
    )

    test_asserts = [
        {"name": "A", "type": "SQLAssert", "storeVersions": False, "params": {}},
        {
            "name": "B",
            "type": "NullAssert",
            "passed": True,
            "storeVersions": False,
            "params": {},
        },
        {"name": "C", "type": "NullAssert", "params": {}},
    ]

    statuses = asserts.run_asserts(test_asserts, {}, "", 0)

    assert statuses["A"] == AssertResult(
        passed=True, actual="foo", expected="foo", description="good"
    )

    assert statuses["B"] == AssertResult(
        passed=True, actual="", expected="", description=""
    )

    assert statuses["C"] == [
        AssertResult(passed=False, actual="", expected="", description="")
    ]
