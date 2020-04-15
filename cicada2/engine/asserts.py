import time
from typing import Dict, List

from cicada2.engine.messaging import send_assert
from cicada2.engine.parsing import render_section
from cicada2.engine.state import create_result_name
from cicada2.engine.types import Assert, AssertResult, Statuses


def run_asserts(asserts: List[Assert], state: dict, hostname: str, seconds_between_asserts: float) -> Statuses:
    results: Statuses = {}

    for asrt in asserts:
        # NOTE: support executionPerCycle?
        rendered_assert: Assert = render_section(asrt, state)

        assert_name: str = rendered_assert.get('name')

        if assert_name is None:
            assert_name = create_result_name(rendered_assert['type'], results)

        assert 'params' in rendered_assert, f"Assert {assert_name} is missing property 'params'"

        if rendered_assert['type'] == 'NullAssert':
            # NOTE: possibly add template free way of computing passed
            # passed: bool = rendered_assert.get('passed', False)
            assert_result = AssertResult(
                passed=rendered_assert.get('passed', False),
                actual=rendered_assert.get('actual', ''),
                expected=rendered_assert.get('expected', ''),
                description=rendered_assert.get('description', '')
            )
        else:
            # passed: bool = send_assert(hostname, rendered_assert)
            assert_result = send_assert(hostname, rendered_assert)

        # Saved as list so versions of the assert call can be stored
        # NOTE: This should be improved, [assert_result] is un-intuitive
        results[assert_name] = [assert_result]

        time.sleep(seconds_between_asserts)

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
        if not any(status['passed'] for status in statuses[assert_name])
    ]
