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


def run_actions(actions: List[Action], state: dict, hostname: str) -> ActionsData:
    def infinite_defaultdict():
        return defaultdict(infinite_defaultdict)

    data: ActionsData = infinite_defaultdict()

    for action in actions:
        rendered_action: Action = render_section(action, state)
        executions_per_cycle: int = rendered_action.get('executionsPerCycle', 1)
        action_results: List[ActionResult] = []

        for _ in range(executions_per_cycle):
            execution_output: ActionResult = send_action(hostname, rendered_action)
            action_results.append(execution_output)

        action_name: str = rendered_action.get('name')

        if action_name is None:
            action_name: str = create_result_name(rendered_action['type'], data)

        data[action_name]['results'] = action_results

        for output in rendered_action.get('outputs', []):
            rendered_output: Output = render_section(
                section=output,
                state=state,
                results=action_results
            )

            # TODO: handle key errors (output may not have name or value)
            # TODO: support for indexed/non-list outputs
            # TODO: support for global outputs
            data[action_name]['outputs'][rendered_output['name']] = (
                rendered_output['value']
            )

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
