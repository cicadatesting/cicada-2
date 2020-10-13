import time
from typing import List

from cicada2.engine.messaging import send_assert
from cicada2.engine.parsing import render_section
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
        rendered_assert: Assert = render_section(asrt, state)

        assert_name = rendered_assert.get("name")
        executions_per_cycle = rendered_assert.get("executionsPerCycle", 1)
        assert_results: List[AssertResult] = []

        if rendered_assert["type"] == "NullAssert":
            for _ in range(executions_per_cycle):
                # NOTE: possibly add template free way of computing passed
                assert_results.append(
                    AssertResult(
                        passed=rendered_assert.get("passed", False),
                        actual=rendered_assert.get("actual", ""),
                        expected=rendered_assert.get("expected", ""),
                        description=rendered_assert.get("description", ""),
                    )
                )
        else:
            assert (
                "params" in rendered_assert
            ), f"Assert {assert_name} is missing property 'params'"

            for _ in range(executions_per_cycle):
                assert_result = send_assert(hostname, rendered_assert)

                if rendered_assert.get("negate", False):
                    assert_result["passed"] = not assert_result.get("passed")

                    if assert_result["passed"]:
                        assert_result[
                            "description"
                        ] = f"passed; negated: {assert_result.get('description')}"
                    else:
                        assert_result[
                            "description"
                        ] = f"expected not {assert_result.get('expected')}"

                assert_results.append(assert_result)

        save_assert_versions = rendered_assert.get("storeVersions", True)

        if not save_assert_versions:
            results[assert_name] = assert_results[-1]
        else:
            results[assert_name] = assert_results

        if i != len(asserts) - 1:
            # Only wait if there is another assert
            time.sleep(seconds_between_asserts)

    return results
