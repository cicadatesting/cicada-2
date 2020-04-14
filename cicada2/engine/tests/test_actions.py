from unittest.mock import patch

from cicada2.engine import actions


@patch('cicada2.engine.actions.send_action')
def test_run_actions(send_action_mock):
    send_action_mock.return_value = {
        'foo': 'bar'
    }

    test_actions = [
        {
            'type': 'POST',
            'executionsPerCycle': 2,
            'params': {
                'foo': 'bar'
            },
            'outputs': [
                {
                    'name': 'A',
                    'value': 'xyz'
                }
            ]
        },
        {
            'name': 'X',
            'params': {
                'fizz': 'buzz'
            }
        }
    ]

    actions_data = actions.run_actions(test_actions, {}, '')

    assert actions_data['POST0']['results'] == [{'foo': 'bar'}, {'foo': 'bar'}]
    assert actions_data['POST0']['outputs']['A'] == ['xyz']
    assert actions_data['X']['results'] == [{'foo': 'bar'}]


@patch('cicada2.engine.actions.send_action')
def test_run_actions_errored_call(send_action_mock):
    send_action_mock.side_effect = [
        {
            'foo': 'bar'
        },
        {},
        {}
    ]

    test_actions = [
        {
            'type': 'POST',
            'executionsPerCycle': 2,
            'params': {
                'foo': 'bar'
            },
            'outputs': [
                {
                    'name': 'A',
                    'value': 'xyz'
                }
            ]
        },
        {
            'name': 'X',
            'params': {
                'fizz': 'buzz'
            }
        }
    ]

    actions_data = actions.run_actions(test_actions, {}, '')

    assert actions_data['POST0']['results'] == [{'foo': 'bar'}, {}]
    assert actions_data['POST0']['outputs']['A'] == ['xyz']
    assert actions_data['X']['results'] == [{}]


def test_combine_action_data():
    current_actions_data = {
        'POST0': {
            'results': [
                {
                    'foo': 'bar'
                },
                {
                    'foo': 'bar'
                }
            ],
            'outputs': {
                'A': ['xyz']
            }
        }
    }

    new_actions_data = {
        'POST0': {
            'results': [
                {
                    'foo': 'bar'
                },
                {
                    'foo': 'bar'
                }
            ],
            'outputs': {
                'A': ['xyz']
            }
        },
        'X': {
            'results': [
                {
                    'foo': 'bar'
                }
            ]
        }
    }

    combined_actions_data = actions.combine_action_data(current_actions_data, new_actions_data)

    assert combined_actions_data['POST0']['results'] == [
        {'foo': 'bar'},
        {'foo': 'bar'},
        {'foo': 'bar'},
        {'foo': 'bar'}
    ]

    assert combined_actions_data['POST0']['outputs']['A'] == ['xyz', 'xyz']
    assert combined_actions_data['X']['results'] == [{'foo': 'bar'}]


def test_combine_action_data_error():
    current_actions_data = {
        'POST0': {
            'results': [
                {
                    'foo': 'bar'
                },
                {
                    'foo': 'bar'
                }
            ],
            'outputs': {
                'A': ['xyz']
            }
        }
    }

    new_actions_data = {
        'POST0': {
            'results': [{}, {}],
            'outputs': {
                'A': ['xyz']
            }
        },
        'X': {
            'results': [
                {
                    'foo': 'bar'
                }
            ]
        }
    }

    combined_actions_data = actions.combine_action_data(current_actions_data, new_actions_data)

    assert combined_actions_data['POST0']['results'] == [
        {'foo': 'bar'},
        {'foo': 'bar'},
        {},
        {}
    ]

    assert combined_actions_data['POST0']['outputs']['A'] == ['xyz', 'xyz']
    assert combined_actions_data['X']['results'] == [{'foo': 'bar'}]
