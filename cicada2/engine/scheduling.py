import os
import time
import json
import uuid
from typing import Dict, List, Optional

from dask.distributed import Client, Future

from cicada2.engine.config import (
    INITIAL_STATE_FILE,
    TASK_TYPE,
    REPORTS_FOLDER,
    TESTS_FOLDER,
)
from cicada2.engine.loading import load_tests_tree
from cicada2.shared.logs import get_logger
from cicada2.engine.reporting import render_report
from cicada2.shared.types import TestSummary


LOGGER = get_logger("scheduling")


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
    test_dependencies: Dict[str, List[str]],
) -> bool:
    # test has not run yet and all dependencies have finished
    return not test_statuses[test_name] and all(
        test_statuses[dep_name] and test_statuses[dep_name].done()
        for dep_name in test_dependencies[test_name]
    )


def all_tests_finished(test_statuses: Dict[str, Optional[Future]]) -> bool:
    return all(
        test_statuses[test_name] and test_statuses[test_name].done()
        for test_name in test_statuses
    )


def run_tests(
    tests_folder: str = TESTS_FOLDER,
    initial_state_file: str = INITIAL_STATE_FILE,
    tasks_type: str = TASK_TYPE,
    reports_location: str = REPORTS_FOLDER,
):
    # NOTE: possibly have run ID in globals
    run_id = f"cicada-2-run-{str(uuid.uuid4())[:8]}"

    LOGGER.info(f"Starting run {run_id}")
    test_configs, test_runners, test_dependencies = load_tests_tree(
        tests_folder, tasks_type, run_id
    )

    if initial_state_file:
        with open(initial_state_file) as initial_state_fp:
            initial_state = json.load(initial_state_fp)
    else:
        initial_state = {}

    client = Client(processes=False)
    # Initialize to None to prevent stopping on first run
    test_statuses: Dict[str, Future] = {test_name: None for test_name in test_runners}

    # Poll for jobs that can be launched based on completed test dependencies
    while not all_tests_finished(test_statuses):
        for test_name in test_statuses:
            if test_is_ready(test_name, test_statuses, test_dependencies):
                # TODO: move to function
                # NOTE: possibly have globals in separate section
                state = {**{"globals": {}}, **initial_state}
                has_missing_dependencies = False

                for test_dependency in test_dependencies[test_name]:
                    # NOTE: dependencies may need ordering in future
                    dependency_result = test_statuses[test_dependency].result()

                    dependency_summary = dependency_result[test_dependency]["summary"]

                    dependency_error = dependency_summary["error"]
                    dependency_remaining_asserts = dependency_summary[
                        "remaining_asserts"
                    ]

                    if dependency_error or dependency_remaining_asserts != []:
                        has_missing_dependencies = True
                    else:
                        state.update(dependency_result)

                if has_missing_dependencies and not test_configs[test_name].get(
                    "runIfFailedDependency", False
                ):
                    test_summary = TestSummary(
                        error="skipped",
                        remaining_asserts=[],
                        completed_cycles=0,
                        duration=0,
                    )

                    test_statuses[test_name] = client.submit(
                        lambda: {**state, **{test_name: {"summary": test_summary}}}
                    )
                else:
                    test_statuses[test_name] = client.submit(
                        test_runners[test_name], state=state
                    )

        # NOTE: Possibly launch tasks with wait on completed
        time.sleep(1)

    LOGGER.debug(f"test statuses: {test_statuses}")

    os.makedirs(reports_location, exist_ok=True)
    final_state = {}

    for test_name in sort_dependencies(test_dependencies):
        final_test_state = test_statuses[test_name].result()

        with open(
            os.path.join(reports_location, f"state.{test_name}.json"), "w"
        ) as final_test_state_fp:
            json.dump(final_test_state, final_test_state_fp, indent=2)

        final_state = {**final_state, **final_test_state}

    report_string = render_report(final_state, run_id=run_id)

    with open(os.path.join(reports_location, "report.md"), "w") as report_fp:
        report_fp.write(report_string)

    with open(
        os.path.join(reports_location, "state.final.json"), "w"
    ) as final_state_fp:
        json.dump(final_state, final_state_fp, indent=2)
