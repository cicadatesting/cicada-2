import re
from typing import Any, Tuple, Collection, Dict, List, Union

from cicada2.shared.types import Assert, AssertResult, Statuses


reserved_keywords = ["all_required", "match", "ordered"]


def assert_dicts(
    expected: dict, actual: dict, all_required=False, **kwargs
) -> Tuple[bool, str]:
    """
    Check if two dicts are equal. If all_required is set to false, make sure
    the expected dict is a subset of the actual dict

    Args:
        expected: Expected dict contents
        actual: Actual dict to check
        all_required: Make sure expected dict is equal to actual dict. Otherwise ensure subset

    Returns:
        Whether or not the dicts match and a description of the findings
    """
    if all_required:
        passed = expected == actual

        if not passed:
            description = f"Expected {expected}, got {actual}"
        else:
            description = "passed"
    else:
        non_matching_items = {}

        for expected_key in expected:
            if expected_key not in actual:
                # NOTE: consider truncating actual dict in error message
                non_matching_items[expected_key] = f"{expected_key} not in {actual}"
                continue

            passed, description = assert_element(
                expected[expected_key],
                actual[expected_key],
                all_required=all_required,
                **kwargs,
            )

            if not passed:
                non_matching_items[expected_key] = description

        passed = non_matching_items == {}

        if not passed:
            description = f"The following items were not found: {non_matching_items}"
        else:
            description = "passed"

    return passed, description


def assert_strings(
    expected: str, actual: str, match=False, **kwargs
) -> Tuple[bool, str]:
    """
    Check if two strings are equal or match an expected regex pattern

    Args:
        expected: The expected string or regex pattern
        actual: The string to match
        match: The expected string is a regex and actual should match it

    Returns:
        Whether the two strings match or equal each other and a description or the result
    """
    if match:
        passed = re.match(
            expected,
            actual,
            **{k: v for k, v in kwargs.items() if k not in reserved_keywords},
        )

        if not passed:
            description = f"{actual} does not match {expected}"
        else:
            description = "passed"
    else:
        passed = expected == actual

        if not passed:
            description = f"Expected {expected}, got {actual}"
        else:
            description = "passed"

    return passed, description


def assert_collections(
    expected: Collection,
    actual: Collection,
    all_required=False,
    ordered=False,
    **kwargs,
) -> Tuple[bool, str]:
    """
    Checks if expected collection fits description of actual collection

    Args:
        expected: The expected collection
        actual:  The actual collection
        all_required: If true, the expected and actual collections must be the same size
        ordered: If true, the expected collection must be in the same order as the first collection

    Returns:
        Whether or not the collections are equivalent and a description regarding that status
    """

    len_expected = len(expected)
    len_actual = len(actual)

    if len_expected > len_actual:
        return False, f"Expected at least {len_expected} elements but got {len_actual}"

    if len_expected != len_actual and all_required:
        return False, f"Expected {len_expected} elements but got {len_actual}"

    if ordered:
        for expected_element, actual_element in zip(expected, actual):
            passed, description = assert_element(
                expected_element,
                actual_element,
                all_required=all_required,
                ordered=ordered,
                **kwargs,
            )

            if not passed:
                return passed, description
    else:
        for expected_element in expected:
            passed, description = False, ""

            for actual_element in actual:
                passed, description = assert_element(
                    expected_element,
                    actual_element,
                    all_required=all_required,
                    ordered=ordered,
                    **kwargs,
                )

                if passed:
                    break

            if not passed:
                return False, f"{expected_element} not found: {description}"

    return True, "passed"


def assert_element(expected: Any, actual: Any, **kwargs) -> Tuple[bool, str]:
    # pylint: disable=bad-option-value,isinstance-second-argument-not-valid-type
    """
    Checks if two elements are equivalent using the default assertion types

    Args:
        expected: The item expected to match
        actual: The actual item to compare to

    Returns:
        Whether or not the elements are equivalent and a description regarding the two
    """
    if isinstance(expected, str) and isinstance(actual, str):
        return assert_strings(expected, actual, **kwargs)
    elif isinstance(expected, dict) and isinstance(actual, dict):
        return assert_dicts(expected, actual, **kwargs)
    elif isinstance(expected, Collection) and isinstance(actual, Collection):
        return assert_collections(expected, actual, **kwargs)
    else:
        passed = expected == actual
        description = "passed"

        if not passed:
            description = f"Expected {expected} but got {actual}"

        return passed, description


def status_is_passed(status: Union[AssertResult, List[AssertResult]]):
    if isinstance(status, list):
        return any(result["passed"] for result in status)
    else:
        return status["passed"]


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
        assert_name = asrt.get("name")

        asserts_by_name[assert_name] = asrt

    # Test has not been run yet for each assert so they're all remaining
    if any(assert_name not in statuses for assert_name in asserts_by_name):
        return asserts

    return [
        asserts_by_name[assert_name]
        for assert_name in asserts_by_name
        if (
            asserts_by_name[assert_name].get("keepIfPassed", False)
            or not status_is_passed(statuses[assert_name])
        )
    ]
