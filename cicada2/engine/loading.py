import os
import yaml
from typing import Dict, List, Iterable, Tuple

from cicada2.engine.errors import ValidationError
from cicada2.engine.runners import run_docker
from cicada2.engine.types import TestConfig, FileTestsConfig, RunnerClosure, TestRunners


def create_test_task(test_config: TestConfig, task_type: str) -> RunnerClosure:
    # NOTE: task must be a callable
    if task_type == 'docker':
        return run_docker(test_config)
    else:
        raise ValidationError(f"Task type {task_type} not found")


def create_test_runners(test_configs: Iterable[TestConfig], task_type: str) -> Dict[str, RunnerClosure]:
    return {
        test_config['name']: create_test_task(
            test_config,
            task_type
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
        task_type: str
) -> TestRunners:
    with open(test_filename, 'r') as test_file:
        main_tests_config: FileTestsConfig = yaml.load(test_file, Loader=yaml.FullLoader)

        test_configs = {}

        for test_config in main_tests_config['tests']:
            assert 'name' in test_config, f"Test {test_config} is missing the property 'name'"
            test_configs[test_config['name']] = test_config

        test_runners = create_test_runners(test_configs.values(), task_type)
        test_dependencies = create_test_dependencies(test_configs.values())

        return TestRunners(
            test_configs=test_configs,
            test_runners=test_runners,
            test_dependencies=test_dependencies
        )


def load_tests_tree(
        tests_folder: str,
        task_type: str
) -> TestRunners:
    test_configs = {}
    test_runners = {}
    test_dependencies = {}

    for root, _, files in os.walk(tests_folder):
        for file in files:
            test_filepath = os.path.abspath(os.path.join(root, file))
            test_file_configs, test_file_runners, test_file_dependencies = load_test_config(test_filepath, task_type)

            test_configs.update(test_file_configs)
            test_runners.update(test_file_runners)
            test_dependencies.update(test_file_dependencies)

    return TestRunners(
        test_configs=test_configs,
        test_runners=test_runners,
        test_dependencies=test_dependencies
    )
