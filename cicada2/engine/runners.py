import uuid
import time
from typing import Dict, Optional

import docker

from cicada2.engine.config import (
    CONTAINER_NETWORK,
    CREATE_NETWORK,
    HEALTHCHECK_INITIAL_WAIT,
    HEALTHCHECK_MAX_RETRIES
)
from cicada2.engine.errors import ValidationError
from cicada2.engine.logs import get_logger
from cicada2.engine.messaging import runner_healthcheck
from cicada2.engine.parsing import render_section
from cicada2.engine.testing import run_test_with_timeout
from cicada2.engine.types import TestConfig, RunnerClosure, TestSummary


LOGGER = get_logger('runners')


def runner_to_image(runner_name: str) -> Optional[str]:
    if runner_name == 'RESTRunner':
        # TODO: update to remote name after pushed
        return 'rest-runner'
    elif runner_name == 'SQLRunner':
        return 'sql-runner'

    return None


def config_to_runner_env(config: Dict[str, str]) -> Dict[str, str]:
    return {
        f"RUNNER_{key.upper()}": config[key]
        for key in config
    }


def container_is_healthy(
        hostname: str,
        initial_wait_time: int = HEALTHCHECK_INITIAL_WAIT,
        max_retries: int = HEALTHCHECK_MAX_RETRIES
) -> bool:
    retries = 0
    wait_time = initial_wait_time

    while retries < max_retries:
        time.sleep(wait_time)
        ready = runner_healthcheck(hostname)

        if not ready:
            retries += 1
            # NOTE: make multiplier configurable too?
            wait_time *= 2
        else:
            return True

    return False


def create_docker_container(
        client: docker.DockerClient,
        image: str,
        env_map: Dict[str, str],
        run_id: str,
        network: str = CONTAINER_NETWORK,
        create_network: bool = CREATE_NETWORK
):
    try:
        try:
            client.networks.get(network)
        except docker.errors.NotFound:
            if create_network:
                client.networks.create(network)
                LOGGER.info(f"Created docker network {network}")
            else:
                raise ValidationError(f"Docker network {network} not configured")
    except docker.errors.APIError as err:
        raise RuntimeError(f"Unable to configure docker network: {err}")

    container_id = f"{image}-{str(uuid.uuid4())[:8]}"

    try:
        # Start container (will pull image if necessary)
        container = client.containers.run(
            image,
            name=container_id,
            detach=True,
            environment=env_map,
            network=network,
            labels=['cicada-2-runner', run_id]
        )
    except docker.errors.APIError as err:
        raise RuntimeError(f"Unable to create container: {err}")

    LOGGER.debug(f"healthchecking container {container.name}")

    if container_is_healthy(f"{container_id}:50051"):
        return container
    else:
        raise RuntimeError('Unable to successfully contact container')


def run_docker(test_config: TestConfig, run_id: str) -> RunnerClosure:
    def closure(state):
        try:
            # TODO: break out docker specific sections
            rendered_test_config = render_section(test_config, state)

            image = (
                runner_to_image(rendered_test_config.get('runner'))
                or rendered_test_config.get('image')
            )

            assert image is not None, "Must specify a valid 'runner' or 'image'"

            env = config_to_runner_env(
                render_section(rendered_test_config.get('config', {}), state)
            )

            client: docker.DockerClient = docker.from_env()
            containers = []

            for _ in range(test_config.get('runnerCount', 1)):
                container = create_docker_container(client, image, env, run_id)
                LOGGER.info(f"successfully created container {container.name}")
                containers.append(container)

            try:
                new_state = run_test_with_timeout(
                    test_config=rendered_test_config,
                    incoming_state=state,
                    hostnames=[f"{container.name}:50051" for container in containers],
                    duration=15
                )
            except (AssertionError, ValueError, TypeError, RuntimeError) as err:
                # NOTE: May need to fine tune exception types
                LOGGER.error(f"Error running test {test_config['name']}: {err}", exc_info=True)

                for container in containers:
                    LOGGER.debug(f"Stopping runner {container.name}")
                    container.stop(timeout=3)

                new_state = {
                    test_config['name']: {
                        'summary': TestSummary(
                            error=str(err),
                            completed_cycles=0,
                            remaining_asserts=[],
                            duration=0
                        )
                    }
                }

            for container in containers:
                LOGGER.debug(f"Stopping runner {container.name}")
                container.stop(timeout=3)
        except (AssertionError, ValueError, TypeError, RuntimeError) as err:
            LOGGER.error(f"Error creating test {test_config['name']}: {err}", exc_info=True)
            new_state = {
                test_config['name']: {
                    'summary': TestSummary(
                        error=str(err),
                        completed_cycles=0,
                        remaining_asserts=[],
                        duration=0
                    )
                }
            }

        return {**state, **new_state}

    return closure
