from typing import Any, Callable, Dict, List, Optional
from typing_extensions import TypedDict


class Output(TypedDict):
    name: str
    isGlobal: bool
    template: str
    value: List[Any]


class Action(TypedDict):
    type: str
    name: str
    template: str
    excecutionsPerCycle: int
    params: dict
    outputs: List[Output]


ActionResult = dict


# NOTE: possibly make this a named tuple
class ActionData(TypedDict):
    results: List[ActionResult]
    outputs: Dict[str, List[Any]]


ActionsData = Dict[str, ActionData]


class Assert(TypedDict):
    name: str
    type: str
    params: dict
    template: str
    passed: bool
    actual: str
    expected: str
    description: str


class AssertResult(TypedDict):
    passed: bool
    actual: Optional[str]
    expected: Optional[str]
    description: Optional[str]


Statuses: object = Dict[str, List[AssertResult]]


class TestConfig(TypedDict):
    name: str
    description: str
    runner: str
    image: str
    actions: List[Action]
    asserts: List[Assert]


class TestSummary(TypedDict):
    completed_cycles: Optional[int]
    remaining_asserts: Optional[List[Assert]]
    error: Optional[str]


class MainTestsConfig(TypedDict):
    description: str
    version: str
    tests: List[TestConfig]


RunnerClosure = Callable[[dict], Optional[dict]]
