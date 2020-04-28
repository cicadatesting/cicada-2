import uuid
import time
from typing import Dict, Optional

import docker

from cicada2.engine.config import (
    CONTAINER_NETWORK,
    CREATE_NETWORK,
    HEALTHCHECK_INITIAL_WAIT,
    HEALTHCHECK_MAX_RETRIES,
)
from cicada2.shared.errors import ValidationError
from cicada2.shared.logs import get_logger
from cicada2.engine.messaging import runner_healthcheck
from cicada2.engine.parsing import render_section
from cicada2.engine.testing import run_test_with_timeout
from cicada2.shared.types import TestConfig, RunnerClosure, TestSummary


LOGGER = get_logger("runners")


def runner_to_image(runner_name: str) -> Optional[str]:
    """
    Determine docker image based on runner name

    Args:
        runner_name: Type of test runner

    Returns:
        Docker image for runner
    """
    if runner_name == "rest-runner":
        return "jeremyaherzog/cicada-2-rest-runner"
    elif runner_name == "sql-runner":
        return "jeremyaherzog/cicada-2-sql-runner"

    return None


def config_to_runner_env(config: Dict[str, str]) -> Dict[str, str]:
    """
    Converts runner config to standard env vars (prefixed with 'RUNNER_')

    Args:
        config: Runner config dictionary

    Returns:
        Formatted env map for runner
    """
    return {f"RUNNER_{key.upper()}": config[key] for key in config}


def container_is_healthy(
    hostname: str,
    initial_wait_time: int = HEALTHCHECK_INITIAL_WAIT,
    max_retries: int = HEALTHCHECK_MAX_RETRIES,
) -> bool:
    """
    Determines if a container is ready to accept messages using an exponential backoff

    Args:
        hostname: Address of runner
        initial_wait_time: Amount of seconds to wait before checking runner
        max_retries: Number of times to check runner

    Returns:
        If the runner is ready
    """
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
    create_network: bool = CREATE_NETWORK,
):
    """
    Creates and configures docker container for docker runner

    Args:
        client: Docker client
        image: docker image to launch
        env_map: env vars to provide to container
        run_id: cicada run ID (to provide as a tag to the container)
        network: Docker network to add container to
        create_network: Creates the network if not found if set to True

    Returns:
        Docker container object
    """
    try:
        try:
            client.networks.get(network)
        except docker.errors.NotFound:
            if create_network:
                client.networks.create(network)
                LOGGER.info("Created docker network %s", network)
            else:
                raise ValidationError(f"Docker network {network} not configured")
    except docker.errors.APIError as err:
        raise RuntimeError(f"Unable to configure docker network: {err}")

    # Parse the part after the last repository path ('/') before the tag (':')
    runner_type = f"{image.split('/')[-1].split(':')[0]}"
    container_id = f"{runner_type}-{str(uuid.uuid4())[:8]}"

    try:
        # Start container (will pull image if necessary)
        container = client.containers.run(
            image,
            name=container_id,
            detach=True,
            environment=env_map,
            network=network,
            labels=["cicada-2-runner", run_id],
        )
    except docker.errors.APIError as err:
        raise RuntimeError(f"Unable to create container: {err}")

    LOGGER.debug("healthchecking container %s", container.name)

    if container_is_healthy(f"{container_id}:50051"):
        return container
    else:
        raise RuntimeError("Unable to successfully contact container")


def run_docker(test_config: TestConfig, run_id: str) -> RunnerClosure:
    """
    Runs test using docker runners

    Args:
        test_config: config of test to run
        run_id: cicada run ID

    Returns:
        Function to run test using state gathered from previous tests
    """

    def closure(state):
        try:
            # TODO: break out docker specific sections
            rendered_test_config = render_section(test_config, state)

            image = runner_to_image(
                rendered_test_config.get("runner")
            ) or rendered_test_config.get("image")

            assert image is not None, "Must specify a valid 'runner' or 'image'"

            env = config_to_runner_env(
                render_section(rendered_test_config.get("config", {}), state)
            )

            # NOTE: client may need more config options
            client: docker.DockerClient = docker.from_env()
            containers = []

            for _ in range(test_config.get("runnerCount", 1)):
                container = create_docker_container(client, image, env, run_id)
                LOGGER.info("successfully created container %s", container.name)
                containers.append(container)

            try:
                new_state = run_test_with_timeout(
                    test_config=rendered_test_config,
                    incoming_state=state,
                    hostnames=[f"{container.name}:50051" for container in containers],
                    duration=rendered_test_config.get("timeout", 15),
                )
            except (AssertionError, ValueError, TypeError, RuntimeError) as err:
                # NOTE: May need to fine tune exception types
                LOGGER.error(
                    "Error running test %s: %s", test_config['name'], err, exc_info=True
                )

                for container in containers:
                    LOGGER.debug("Stopping runner %s", container.name)
                    container.stop(timeout=3)

                new_state = {
                    test_config["name"]: {
                        "summary": TestSummary(
                            description=test_config.get('description'),
                            error=str(err),
                            completed_cycles=0,
                            remaining_asserts=[],
                            duration=0,
                        )
                    }
                }

            for container in containers:
                LOGGER.debug("Stopping runner %s", container.name)
                container.stop(timeout=3)
        except (AssertionError, ValueError, TypeError, RuntimeError) as err:
            LOGGER.error(
                "Error creating test %s: %s", test_config['name'], err, exc_info=True
            )
            new_state = {
                test_config["name"]: {
                    "summary": TestSummary(
                        description=test_config.get('description'),
                        error=str(err),
                        completed_cycles=0,
                        remaining_asserts=[],
                        duration=0,
                    )
                }
            }

        return {**state, **new_state}

    return closure
