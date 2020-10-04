import time
from collections import defaultdict
from typing import List, Set

from cicada2.engine.messaging import send_action
from cicada2.engine.parsing import render_section
from cicada2.engine.state import (
    combine_keys,
    combine_data_by_key,
    combine_datas,
)
from cicada2.shared.types import Action, ActionsData, ActionResult, Output


def run_actions(
    actions: List[Action], state: dict, hostname: str, seconds_between_actions: float
) -> ActionsData:
    """
    Runs a list of actions assigned to a single runner

    Args:
        actions: List of actions to run
        state: Incoming state to use in rendering actions
        hostname: Address of runner
        seconds_between_actions: Seconds to wait between running next action in list

    Returns:
        ActionsData per action provided
    """

    def infinite_defaultdict():
        return defaultdict(infinite_defaultdict)

    data: ActionsData = infinite_defaultdict()

    for i, action in enumerate(actions):
        rendered_action: Action = render_section(action, state)

        action_name = rendered_action.get("name")

        assert (
            "params" in rendered_action
        ), f"Action {action_name} is missing property 'params'"

        executions_per_cycle: int = rendered_action.get("executionsPerCycle", 1)
        action_results: List[ActionResult] = []

        for _ in range(executions_per_cycle):
            execution_output: ActionResult = send_action(hostname, rendered_action)
            action_results.append(execution_output)

            # TODO: run asserts under action here
            # TODO: Add assert statuses to return container
            # TODO: update remaining assert filter and continue running in testing

            time.sleep(rendered_action.get("secondsBetweenExecutions", 0))

        store_action_versions = rendered_action.get("storeVersions", True)

        if not store_action_versions and action_results:
            data[action_name]["results"] = action_results[-1]
        else:
            data[action_name]["results"] = action_results

        for output in rendered_action.get("outputs", []):
            rendered_output: Output = render_section(
                section=output, state=state, results=action_results
            )

            assert (
                "name" in rendered_output
            ), "Output section must have parameter 'name'"
            assert (
                "value" in rendered_output
            ), "Output section must have parameter 'value'"

            # NOTE: support updating outputs in globals section?
            store_output_versions = rendered_output.get("storeVersions", False)

            if not store_output_versions:
                data[action_name]["outputs"][rendered_output["name"]] = rendered_output[
                    "value"
                ]
            else:
                data[action_name]["outputs"][rendered_output["name"]] = [
                    rendered_output["value"]
                ]

        if i != len(actions) - 1:
            # Only wait if there is another action
            time.sleep(seconds_between_actions)

    return data


def combine_action_data(
    combined_data: ActionsData, action_data: ActionsData
) -> ActionsData:
    """
    Combine outputs and results with existing state or of multiple run_action results

    Args:
        combined_data: Initial data that has already been combined (or empty)
        action_data: Action data from a single run_action result

    Returns:
        Existing data combined with one runner's run_action result (does not overwrite combined_data)
    """
    combined_keys: Set[str] = combine_keys(combined_data, action_data)

    return {
        key: {
            "results": combine_datas(
                combined_data.get(key, {}).get("results", []),
                action_data.get(key, {}).get("results", []),
            ),
            "outputs": combine_data_by_key(
                combined_data.get(key, {}).get("outputs", {}),
                action_data.get(key, {}).get("outputs", {}),
            ),
        }
        for key in combined_keys
    }
