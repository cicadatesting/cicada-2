import time
from typing import Dict, List, Optional

from dask.distributed import Client, Future

from cicada2.engine.loading import load_test_runners_tree


def sort_dependencies(dependency_map: Dict[str, List[str]]) -> List[str]:
    added_names = set()
    sorted_names = []

    def add_name(name):
        for dependency_name in dependency_map[name]:
            add_name(dependency_name)

        if name not in added_names:
            added_names.add(name)
            sorted_names.append(name)

    for test_name in dependency_map:
        add_name(test_name)

    return sorted_names


def test_is_ready(
        test_name: str,
        test_statuses: Dict[str, Optional[Future]],
        test_dependencies: Dict[str, List[str]]
) -> bool:
    # test has not run yet and all dependencies have finished
    # TODO: Run task but fail immediately if previous test failed
    return (
        not test_statuses[test_name]
        and all(
            test_statuses[dep_name] and test_statuses[dep_name].done()
            for dep_name in test_dependencies[test_name]
        )
    )


def all_tests_finished(test_statuses: Dict[str, Optional[Future]]) -> bool:
    return all(
        test_statuses[test_name] and test_statuses[test_name].done()
        for test_name in test_statuses
    )


def run_tests(tests_folder: str, tasks_type: str):
    test_runners, test_dependencies = load_test_runners_tree(tests_folder, tasks_type)

    client = Client(processes=False)
    # Initialize to None to prevent stopping on first run
    test_statuses = {test_name: None for test_name in test_runners}

    # Poll for jobs that can be launched based on completed test dependencies
    while not all_tests_finished(test_statuses):
        for test_name in test_statuses:
            # print(f"{test_name} is ready: {test_is_ready(test_name, test_statuses, test_dependencies)}")
            if test_is_ready(test_name, test_statuses, test_dependencies):
                inital_state = {}
                has_missing_dependencies = False

                for test_dependency in test_dependencies[test_name]:
                    # NOTE: dependencies may need ordering in future
                    dependency_result = test_statuses[test_dependency].result()

                    if dependency_result is None:
                        has_missing_dependencies = True
                    else:
                        inital_state.update(dependency_result)

                # TODO: Skip if does not allow passthrough (need test config)
                if has_missing_dependencies:
                    test_statuses[test_name] = client.submit(
                        lambda: None
                    )
                else:
                    # TODO: save state to file
                    test_statuses[test_name] = client.submit(
                        test_runners[test_name],
                        state=inital_state
                    )

        # TODO: launch tasks with wait on completed
        time.sleep(1)

    print(f"test statuses: {test_statuses}")
    final_state = {}

    for test_name in sort_dependencies(test_dependencies):
        final_state[test_name] = test_statuses[test_name].result()

    print(f"final state: {final_state}")
