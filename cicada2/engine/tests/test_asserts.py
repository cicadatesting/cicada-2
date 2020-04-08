from unittest.mock import patch

from cicada2.engine import asserts
from cicada2.engine.types import AssertResult


@patch('cicada2.engine.asserts.send_assert')
def test_run_asserts(mock_send_assert):
    mock_send_assert.return_value = AssertResult(
        passed=True,
        actual='foo',
        expected='foo',
        description='good'
    )

    test_asserts = [
        {
            'name': 'A',
            'type': 'SQLAssert'
        },
        {
            'name': 'B',
            'type': 'NullAssert',
            'passed': True
        },
        {
            'name': 'C',
            'type': 'NullAssert'
        }
    ]

    statuses = asserts.run_asserts(test_asserts, {}, '')

    assert statuses['A'] == [
        AssertResult(
            passed=True,
            actual='foo',
            expected='foo',
            description='good'
        )
    ]

    assert statuses['B'] == [
        AssertResult(passed=True, actual='', expected='', description='')
    ]

    assert statuses['C'] == [
        AssertResult(passed=False, actual='', expected='', description='')
    ]

# TODO: test remote assert errors


def test_get_remaining_asserts():
    test_asserts = [
        {
            'name': 'A'
        },
        {
            'type': 'B'
        },
        {
            'type': 'B'
        },
        {
            'type': 'C',
        }
    ]

    statuses = {
        'A': [
            AssertResult(passed=False, actual='', expected='', description=''),
            AssertResult(passed=True, actual='', expected='', description='')
        ],
        'B0': [
            AssertResult(passed=True, actual='', expected='', description=''),
            AssertResult(passed=True, actual='', expected='', description='')
        ],
        'B1': [
            AssertResult(passed=False, actual='', expected='', description=''),
            AssertResult(passed=False, actual='', expected='', description='')
        ],
        'C0': [
            AssertResult(passed=False, actual='', expected='', description='')
        ]
    }

    remaining_asserts = asserts.get_remaining_asserts(test_asserts, statuses)

    assert len(remaining_asserts) == 2
    assert {'type': 'B'} in remaining_asserts
    assert {'type': 'C'} in remaining_asserts


def test_get_remaining_asserts_no_status():
    test_asserts = [
        {
            'name': 'A'
        },
        {
            'type': 'B'
        },
        {
            'type': 'B'
        },
        {
            'type': 'C',
        }
    ]

    remaining_asserts = asserts.get_remaining_asserts(test_asserts, {})

    assert remaining_asserts == test_asserts
