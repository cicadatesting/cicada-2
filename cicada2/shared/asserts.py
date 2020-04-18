from typing import Tuple


def assert_dicts(
        expected: dict,
        actual: dict,
        all_required=False
) -> Tuple[bool, str]:
    if all_required:
        passed = expected == actual

        if not passed:
            description = f"Expected {expected}, got {actual}"
        else:
            description = 'passed'

        return passed, description
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
            description = 'passed'

        return passed, description
