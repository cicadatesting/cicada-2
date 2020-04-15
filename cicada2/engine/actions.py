import time
from collections import defaultdict
from typing import List, Set

from cicada2.engine.messaging import send_action
from cicada2.engine.parsing import render_section
from cicada2.engine.state import (
    combine_keys,
    combine_lists_by_key,
    create_result_name
)
from cicada2.engine.types import Action, ActionsData, ActionResult, Output


def run_actions(actions: List[Action], state: dict, hostname: str, seconds_between_actions: float) -> ActionsData:
    def infinite_defaultdict():
        return defaultdict(infinite_defaultdict)

    data: ActionsData = infinite_defaultdict()

    for action in actions:
        rendered_action: Action = render_section(action, state)

        action_name: str = rendered_action.get('name')

        if action_name is None:
            action_name: str = create_result_name(rendered_action['type'], data)

        assert 'params' in rendered_action, f"Action {action_name} is missing property 'params'"

        executions_per_cycle: int = rendered_action.get('executionsPerCycle', 1)
        action_results: List[ActionResult] = []

        for _ in range(executions_per_cycle):
            execution_output: ActionResult = send_action(hostname, rendered_action)
            action_results.append(execution_output)

            time.sleep(rendered_action.get('secondsBetweenExecutions', 0))

        data[action_name]['results'] = action_results

        for output in rendered_action.get('outputs', []):
            rendered_output: Output = render_section(
                section=output,
                state=state,
                results=action_results
            )

            assert 'name' in rendered_output, "Output section must have parameter 'name'"
            assert 'value' in rendered_output, "Output section must have parameter 'value'"

            # TODO: support for outputs that overwrite value
            # TODO: support for global outputs
            data[action_name]['outputs'][rendered_output['name']] = [rendered_output['value']]

        time.sleep(seconds_between_actions)

    return data


def combine_action_data(combined_data: ActionsData, action_data: ActionsData) -> ActionsData:
    combined_keys: Set[str] = combine_keys(combined_data, action_data)

    return {
        key: {
            'results': (
                combined_data.get(key, {}).get('results', [])
                + action_data.get(key, {}).get('results', [])
            ),
            'outputs': combine_lists_by_key(
                combined_data.get(key, {}).get('outputs', {}),
                action_data.get(key, {}).get('outputs', {})
            )
        }
        for key in combined_keys
    }
