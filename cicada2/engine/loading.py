import os
import yaml
from typing import Dict, List, Iterable

from cicada2.shared.errors import ValidationError
from cicada2.engine.runners import run_docker
from cicada2.shared.types import TestConfig, FileTestsConfig, RunnerClosure, TestRunners


def create_test_task(test_config: TestConfig, task_type: str, run_id: str) -> RunnerClosure:
    """
    Create runner closure for test

    Args:
        test_config: Test config to create closure for
        task_type: Type of runner service
        run_id: cicada run ID

    Returns:
        Runner closure for test
    """
    if task_type == 'docker':
        return run_docker(test_config, run_id)
    else:
        raise ValidationError(f"Task type {task_type} not found")


def create_test_runners(test_configs: Iterable[TestConfig], task_type: str, run_id: str) -> Dict[str, RunnerClosure]:
    """
    Creates runner closures for multiple tests

    Args:
        test_configs: Tests to create runners for
        task_type: Runner service type
        run_id: cicada run ID

    Returns:
        Map of runner closures by test name
    """
    return {
        test_config['name']: create_test_task(
            test_config,
            task_type,
            run_id
        )
        for test_config in test_configs
    }


def create_test_dependencies(test_configs: Iterable[TestConfig]) -> Dict[str, List[str]]:
    return {
        test_config['name']: test_config.get('dependencies', [])
        for test_config in test_configs
    }


def load_test_config(
        test_filename: str,
        task_type: str,
        run_id: str
) -> TestRunners:
    """
    Loads test config for a file and loads test configs, creates runner_closures, and determines dependencies

    Args:
        test_filename: Path to test file
        task_type: Runner service type
        run_id: cicada run ID

    Returns:
        Test configs, runners and dependencies for test file
    """
    with open(test_filename, 'r') as test_file:
        # TODO: add test filename to report
        main_tests_config: FileTestsConfig = yaml.load(test_file, Loader=yaml.FullLoader)

        test_configs = {}

        for test_config in main_tests_config['tests']:
            assert 'name' in test_config, f"Test {test_config} is missing the property 'name'"
            test_configs[test_config['name']] = test_config

        test_runners = create_test_runners(test_configs.values(), task_type, run_id)
        test_dependencies = create_test_dependencies(test_configs.values())

        return TestRunners(
            test_configs=test_configs,
            test_runners=test_runners,
            test_dependencies=test_dependencies
        )


def load_tests_tree(
        tests_folder: str,
        task_type: str,
        run_id: str
) -> TestRunners:
    """
    Loads tests recursively given a directory containing test files

    Args:
        tests_folder: Path to folder containing test files
        task_type: Runner service type
        run_id: cicada run ID

    Returns:
        Test configs, runners and dependencies for test files under test directory
    """
    test_configs = {}
    test_runners = {}
    test_dependencies = {}

    for root, _, files in os.walk(tests_folder):
        for file in [file for file in files if file.endswith('.cicada.yaml')]:
            test_filepath = os.path.abspath(os.path.join(root, file))
            test_file_configs, test_file_runners, test_file_dependencies = load_test_config(
                test_filepath,
                task_type,
                run_id
            )

            test_configs.update(test_file_configs)
            test_runners.update(test_file_runners)
            test_dependencies.update(test_file_dependencies)

    return TestRunners(
        test_configs=test_configs,
        test_runners=test_runners,
        test_dependencies=test_dependencies
    )
