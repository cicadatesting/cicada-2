import os
import yaml
from typing import Dict, List, Optional, Tuple

from cicada2.engine.runners import run_docker
from cicada2.engine.types import TestConfig, MainTestsConfig, RunnerClosure


def create_test_task(test_config: TestConfig, task_type: str) -> Optional[RunnerClosure]:
    # NOTE: task must be a callable
    if task_type == 'docker':
        return run_docker(test_config)
    else:
        # TODO: return validation info or throw error
        return None


def create_test_runners(main_tests_config: MainTestsConfig, task_type: str) -> Dict[str, Optional[RunnerClosure]]:
    return {
        test_config['name']: create_test_task(
            test_config,
            task_type
        )
        for test_config in main_tests_config['tests']
    }


def create_test_dependencies(main_tests_config: MainTestsConfig) -> Dict[str, List]:
    return {
        test_config['name']: test_config.get('dependencies', [])
        for test_config in main_tests_config['tests']
    }


def load_test_runners(
        test_filename: str,
        task_type: str
) -> Tuple[Dict[str, Optional[RunnerClosure]], Dict[str, List]]:
    with open(test_filename, 'r') as test_file:
        main_tests_config: MainTestsConfig = yaml.load(test_file, Loader=yaml.FullLoader)

        # TODO: other possible metadata handling
        test_runners = create_test_runners(main_tests_config, task_type)
        test_dependencies = create_test_dependencies(main_tests_config)

        return test_runners, test_dependencies


def load_test_runners_tree(
        tests_folder: str,
        tasks_type: str
) -> Tuple[Dict[str, Optional[RunnerClosure]], Dict[str, List]]:
    test_runners = {}
    test_dependencies = {}

    for root, _, files in os.walk(tests_folder):
        for file in files:
            test_filepath = os.path.abspath(os.path.join(root, file))
            test_file_runners, test_file_dependencies = load_test_runners(
                test_filepath, tasks_type
            )

            test_runners.update(test_file_runners)
            test_dependencies.update(test_file_dependencies)

    return test_runners, test_dependencies
