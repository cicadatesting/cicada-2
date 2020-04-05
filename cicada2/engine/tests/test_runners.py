from unittest.mock import patch

from cicada2.engine import runners


def test_config_to_runner_env():
    config = {
        'foo': 'bar',
        'fizz': 'buzz'
    }

    env_config = runners.config_to_runner_env(config)

    assert env_config == {
        'RUNNER_FOO': 'bar',
        'RUNNER_FIZZ': 'buzz'
    }


@patch('cicada2.engine.runners.runner_healthcheck')
def test_runner_healthcheck_success(runner_healthcheck_mock):
    runner_healthcheck_mock.side_effect = [False, False, True]

    assert runners.container_is_healthy(
        hostname='alpha',
        initial_wait_time=0,
        max_retries=3
    )


@patch('cicada2.engine.runners.runner_healthcheck')
def test_runner_healthcheck_failure(runner_healthcheck_mock):
    runner_healthcheck_mock.return_value = False

    assert not runners.container_is_healthy(
        hostname='alpha',
        initial_wait_time=0,
        max_retries=3
    )
