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


class ActionData(TypedDict):
    results: List[ActionResult]
    outputs: Dict[str, List[Any]]


ActionsData = Dict[str, ActionData]


class Assert(TypedDict):
    name: str
    type: str
    params: dict
    template: str


Statuses: object = Dict[str, List[bool]]


class TestConfig(TypedDict):
    name: str
    description: str
    runner: str
    image: str
    actions: List[Action]
    asserts: List[Assert]


class MainTestsConfig(TypedDict):
    description: str
    version: str
    tests: List[TestConfig]


RunnerClosure = Callable[[dict], Optional[dict]]
