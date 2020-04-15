from typing import Any, Callable, Dict, List, NamedTuple, Optional
from typing_extensions import TypedDict


class Output(TypedDict):
    name: str
    isGlobal: bool
    template: str
    value: List[Any]


class Action(TypedDict):
    type: str
    name: Optional[str]  # NOTE: should this be set in the background if type is set but not name?
    template: Optional[str]
    excecutionsPerCycle: Optional[int]
    secondsBetweenExecutions: Optional[float]
    params: dict
    outputs: Optional[List[Output]]


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
    runIfFailedDependency: Optional[bool]
    description: Optional[str]  # TODO: add to report
    runner: Optional[str]
    image: Optional[str]
    actions: Optional[List[Action]]
    asserts: Optional[List[Assert]]
    secondsBetweenCycles: Optional[float]
    secondsBetweenActions: Optional[float]
    secondsBetweenAsserts: Optional[float]


class TestSummary(TypedDict):
    # TODO: report total test runtime
    completed_cycles: Optional[int]
    remaining_asserts: Optional[List[Assert]]
    error: Optional[str]


class FileTestsConfig(TypedDict):
    description: str
    version: str
    tests: List[TestConfig]


RunnerClosure = Callable[[dict], Optional[dict]]


class TestRunners(NamedTuple):
    test_configs: Dict[str, TestConfig]
    test_runners: Dict[str, RunnerClosure]
    test_dependencies: Dict[str, List[str]]
