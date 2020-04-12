import uuid
import time
from typing import Dict, Optional

import docker

from cicada2.engine.messaging import runner_healthcheck
from cicada2.engine.parsing import render_section
from cicada2.engine.testing import run_test_with_timeout
from cicada2.engine.types import TestConfig, RunnerClosure, TestSummary


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


def container_is_healthy(hostname: str, initial_wait_time: int = 2, max_retries: int = 5) -> bool:
    # healthcheck container/exponential backoff
    # TODO: make configurable
    retries = 0
    wait_time = initial_wait_time

    while retries < max_retries:
        time.sleep(wait_time)
        ready = runner_healthcheck(hostname)

        if not ready:
            retries += 1
            wait_time *= 2
        else:
            return True

    return False


def create_docker_container(client: docker.DockerClient, image: str, env_map: Dict[str, str]):
    container_id = f"{image}-{str(uuid.uuid4())[:8]}"

    try:
        # Start container (will pull image if necessary)
        # TODO: label containers with cicada-2-runner and some run ID
        container = client.containers.run(
            image,
            name=container_id,
            detach=True,
            environment=env_map,
            network='cicada-2',  # TODO: make configurable, ensure network exists
        )
    except docker.errors.APIError as err:
        # TODO: custom error
        raise RuntimeError(f"Unable to create container: {err}")

    print(f"healthchecking container {container.name}")

    if container_is_healthy(f"{container_id}:50051"):
        return container
    else:
        raise RuntimeError('Unable to successfully contact container')


def run_docker(test_config: TestConfig) -> RunnerClosure:
    def closure(state):
        client: docker.DockerClient = docker.from_env()
        # TODO: error if no image found
        image = (
            runner_to_image(test_config.get('runner'))
            or test_config['image']
        )

        env = config_to_runner_env(
            render_section(test_config.get('config', {}), state)
        )

        # TODO: create all containers here (based on runnerCount)
        container = create_docker_container(client, image, env)
        print(f"successfully created container {container.name}")

        try:
            new_state = run_test_with_timeout(
                test_config=test_config,
                incoming_state=state,
                hostnames=[f"{container.name}:50051"],
                duration=15
            )
        except Exception as err:
            # TODO: fine tune exception types
            print(err)
            container.stop()
            new_state = {
                test_config['name']: {
                    'summary': TestSummary(
                        error=str(err),
                        completed_cycles=0,
                        remaining_asserts=[]
                    )
                }
            }

        container.stop()

        # call test runner with container address
        # Return new state with updates
        return {**state, **new_state}

    return closure
