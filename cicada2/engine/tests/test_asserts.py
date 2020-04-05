from unittest.mock import patch

from cicada2.engine import asserts


@patch('cicada2.engine.asserts.send_assert')
def test_run_asserts(mock_send_assert):
    mock_send_assert.return_value = True

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

    assert statuses['A'] == [True]
    assert statuses['B'] == [True]
    assert statuses['C'] == [False]

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
        'A': [False, True],
        'B0': [True, True],
        'B1': [False, False],
        'C0': [False]
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
