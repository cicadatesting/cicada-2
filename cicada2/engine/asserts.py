from typing import Dict, List

from cicada2.engine.messaging import send_assert
from cicada2.engine.parsing import render_section
from cicada2.engine.state import create_result_name
from cicada2.engine.types import Assert, Statuses


def run_asserts(asserts: List[Assert], state: dict, hostname: str) -> Statuses:
    results: Statuses = {}

    for asrt in asserts:
        # TODO: support executionPerCycle?
        rendered_assert: Assert = render_section(asrt, state)

        # TODO: validate for action/assert having type param
        if rendered_assert['type'] == 'NullAssert':
            # NOTE: possibly add template free way of computing passed
            passed: bool = rendered_assert.get('passed', False)
        else:
            passed: bool = send_assert(hostname, rendered_assert)

        assert_name: str = rendered_assert.get('name')

        if assert_name is None:
            assert_name = create_result_name(rendered_assert['type'], results)

        # NOTE: This should be improved, [passed] is un-intuitive
        results[assert_name] = [passed]

    return results


def get_remaining_asserts(asserts: List[Assert], statuses: Statuses) -> List[Assert]:
    asserts_by_name: Dict[str, Assert] = {}

    for asrt in asserts:
        assert_name: str = asrt.get('name')

        if assert_name is None:
            assert_name = create_result_name(asrt['type'], asserts_by_name)

        asserts_by_name[assert_name] = asrt

    if any(assert_name not in statuses for assert_name in asserts_by_name):
        return asserts

    return [
        asserts_by_name[assert_name]
        for assert_name in asserts_by_name
        if not any(statuses[assert_name])
    ]
