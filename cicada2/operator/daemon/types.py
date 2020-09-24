from typing import Dict, List, TypedDict


class Dependency(TypedDict):
    name: str
    labels: Dict[str, str]
    statuses: List[str]


class SetupConfig(TypedDict):
    pvc: str
    mountPath: str
    remotePath: str
    localPath: str


class Spec(TypedDict):
    dependencies: List[Dependency]
    ioConfig: Dict[str, str]
    engineConfig: Dict[str, str]
    tests: SetupConfig
    reports: SetupConfig


class Metadata(TypedDict):
    name: str
    namespace: str


class TestEngineBody(TypedDict):
    metadata: Metadata
    spec: Spec
