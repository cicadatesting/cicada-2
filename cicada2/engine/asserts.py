import time
from typing import Dict, List

from cicada2.engine.messaging import send_assert
from cicada2.engine.parsing import render_section
from cicada2.engine.state import create_item_name
from cicada2.shared.types import Assert, AssertResult, Statuses


def run_asserts(
    asserts: List[Assert], state: dict, hostname: str, seconds_between_asserts: float
) -> Statuses:
    """
    Run asserts assigned to host

    Args:
        asserts: List of asserts assigned to host
        state: Test state to pass to templates
        hostname: Host name to send assert data to
        seconds_between_asserts: Time to wait in between running each assert

    Returns:
        Statuses of all asserts run by host
    """
    results: Statuses = {}

    for i, asrt in enumerate(asserts):
        # TODO: support executions per cycle
        rendered_assert: Assert = render_section(asrt, state)

        assert_name: str = rendered_assert.get("name")

        if assert_name is None:
            assert_name = create_item_name(rendered_assert["type"], results)

        if rendered_assert["type"] == "NullAssert":
            # NOTE: possibly add template free way of computing passed
            assert_result = AssertResult(
                passed=rendered_assert.get("passed", False),
                actual=rendered_assert.get("actual", ""),
                expected=rendered_assert.get("expected", ""),
                description=rendered_assert.get("description", ""),
            )
        else:
            assert (
                "params" in rendered_assert
            ), f"Assert {assert_name} is missing property 'params'"

            assert_result = send_assert(hostname, rendered_assert)

        save_assert_versions = rendered_assert.get("storeVersions", True)

        if not save_assert_versions:
            results[assert_name] = assert_result
        else:
            results[assert_name] = [assert_result]

        if i != len(asserts) - 1:
            # Only wait if there is another assert
            time.sleep(seconds_between_asserts)

    return results


def get_remaining_asserts(asserts: List[Assert], statuses: Statuses) -> List[Assert]:
    """
    Returns the asserts that haven't passed yet or should still be run

    Args:
        asserts: List of asserts in test
        statuses: Statuses of each assert

    Returns:
        List of asserts that still need to run
    """
    asserts_by_name: Dict[str, Assert] = {}

    for asrt in asserts:
        assert_name: str = asrt.get("name")

        if assert_name is None:
            assert_name = create_item_name(asrt["type"], asserts_by_name)

        asserts_by_name[assert_name] = asrt

    # Test has not been run yet for each assert so they're all remaining
    if any(assert_name not in statuses for assert_name in asserts_by_name):
        return asserts

    return [
        asserts_by_name[assert_name]
        for assert_name in asserts_by_name
        if (
            asserts_by_name[assert_name].get("keepIfPassed", False)
            or not any(status["passed"] for status in statuses[assert_name])
        )
    ]
