from typing import Any, Callable, Dict, List, NamedTuple, Optional, Union
from typing_extensions import TypedDict

# TODO: investigate dataclass usage


class Assert(TypedDict):
    name: Optional[str]
    type: str
    executionsPerCycle: Optional[int]
    params: Optional[dict]
    template: Optional[str]
    passed: Optional[bool]
    keepIfPassed: Optional[bool]
    actual: Optional[str]
    expected: Optional[str]
    description: Optional[str]
    storeVersions: Optional[bool]
    assertOptions: Optional[dict]
    negate: Optional[bool]


class AssertResult(TypedDict):
    passed: bool
    actual: Optional[str]
    expected: Optional[str]
    description: Optional[str]


class Output(TypedDict):
    name: str
    # isGlobal: Optional[bool]
    template: Optional[str]
    storeVersions: Optional[bool]
    value: List[Any]


class Action(TypedDict):
    type: str
    name: Optional[str]
    template: Optional[str]
    excecutionsPerCycle: Optional[int]
    secondsBetweenExecutions: Optional[float]
    storeVersions: Optional[bool]
    params: dict
    asserts: Optional[List[Assert]]
    outputs: Optional[List[Output]]


ActionResult = dict


# NOTE: possibly make this a named tuple
class ActionData(TypedDict):
    results: Union[ActionResult, List[ActionResult]]
    outputs: Dict[str, Union[Any, List[Any]]]


ActionsData = Dict[str, ActionData]


Statuses: object = Dict[str, Union[AssertResult, List[AssertResult]]]


class Volume(TypedDict):
    source: str
    destination: str


class TestConfig(TypedDict):
    name: str
    timeout: Optional[float]  # NOTE: possibly take in ms instead of fraction of seconds
    template: Optional[str]
    cycles: int
    runIfFailedDependency: Optional[bool]
    description: Optional[str]
    runner: Optional[str]
    runnerCount: Optional[str]
    image: Optional[str]
    volumes: Optional[List[Volume]]
    config: Dict[str, str]
    actions: Optional[List[Action]]
    asserts: Optional[List[Assert]]
    secondsBetweenCycles: Optional[float]
    secondsBetweenActions: Optional[float]
    secondsBetweenAsserts: Optional[float]
    dependencies: List[str]
    actionDistributionStrategy: str
    assertDistributionStrategy: str


class TestSummary(TypedDict):
    description: Optional[str]
    completed_cycles: int
    remaining_asserts: List[str]
    error: Optional[str]
    duration: int


class FileTestsConfig(TypedDict):
    description: str
    version: str
    tests: List[TestConfig]


RunnerClosure = Callable[[dict], Optional[dict]]


class TestRunners(NamedTuple):
    test_configs: Dict[str, TestConfig]
    test_runners: Dict[str, RunnerClosure]
    test_dependencies: Dict[str, List[str]]
