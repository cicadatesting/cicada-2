import re
from typing import Tuple


def assert_dicts(expected: dict, actual: dict, all_required=False) -> Tuple[bool, str]:
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
        passed = expected.items() <= actual.items()

        if not passed:
            non_matching_items = {
                item[0]: item[1]
                for item in expected.items()
                if item not in actual.items()
            }

            description = f"Expected {non_matching_items} to be in {actual}"
        else:
            description = "passed"

    return passed, description


def assert_strings(expected: str, actual: str, match=False) -> Tuple[bool, str]:
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
        passed = re.match(expected, actual)

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
