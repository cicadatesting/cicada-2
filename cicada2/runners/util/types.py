from typing import NamedTuple


class AssertResult(NamedTuple):
    passed: bool
    actual: str
    expected: str
    description: str
