from os import getenv
from datetime import datetime
from typing import Dict, Optional, Union
from typing_extensions import TypedDict
from uuid import uuid4
from filecmp import cmp

import boto3
from boto3_type_annotations.s3 import Client
from s3fs import S3FileSystem

from cicada2.shared.types import AssertResult
from cicada2.shared.asserts import assert_strings


class ActionParams(TypedDict):
    path: Optional[str]
    contents: Optional[str]
    sourcePath: Optional[str]
    destinationPath: Optional[str]
    recursive: Optional[bool]
    bucketName: Optional[str]


class ActionResponse(TypedDict):
    runtime: int


class ReadResponse(ActionResponse):
    contents: Optional[str]


class ExistsResponse(ActionResponse):
    exists: bool


class AssertParams(TypedDict):
    expected: Union[bool, str]
    path: Optional[str]
    actionParams: ActionParams


def extract_s3_config() -> Dict[str, Optional[str]]:
    return {
        "endpoint_url": getenv("RUNNER_ENDPOINTURL"),
        "region_name": getenv("RUNNER_REGION"),
    }


def extract_client_config() -> Dict[str, Union[Optional[str], bool]]:
    return {
        "aws_access_key_id": getenv("RUNNER_ACCESSKEYID"),
        "aws_secret_access_key": getenv("RUNNER_SECRETACCESSKEY"),
        "aws_session_token": getenv("RUNNER_SESSIONTOKEN"),
        "use_ssl": getenv("RUNNER_USESSL", True),
    }


def s3fs_client() -> S3FileSystem:
    client_config = extract_client_config()

    return S3FileSystem(
        key=client_config["aws_access_key_id"],
        secret=client_config["aws_secret_access_key"],
        token=client_config["aws_session_token"],
        use_ssl=client_config["use_ssl"],
        client_kwargs=extract_s3_config(),
    )


def boto3_client() -> Client:
    return boto3.client("s3", **extract_s3_config(), **extract_client_config())


def write_contents(path: str, contents: str, client: S3FileSystem):
    with client.open(path, "w") as fp:
        fp.write(contents)


def get_contents(path: str, client: S3FileSystem) -> Optional[str]:
    if not client.exists(path):
        return None

    with client.open(path, "r") as fp:
        return fp.read()


def run_action(action_type: str, params: ActionParams) -> Union[ActionResponse, ReadResponse, ExistsResponse]:
    if action_type == "write":
        assert "path" in params, "'path' must be specified for action 'write'"
        assert (
            "contents" in params
        ), "'contents' must be specified for action 'contents'"

        path = params["path"]
        contents = params["contents"]
        client = s3fs_client()

        start = datetime.now()
        write_contents(path, contents, client)
        end = datetime.now()

        return ActionResponse(runtime=int((end - start).microseconds / 1000))
    elif action_type == "read":
        assert "path" in params, "'path' must be specified for action 'read'"

        path = params["path"]
        client = s3fs_client()

        start = datetime.now()
        contents = get_contents(path, client)
        end = datetime.now()

        # NOTE: special support JSON files?
        return ReadResponse(contents=contents, runtime=int((end - start).microseconds / 1000))
    elif action_type == "exists":
        assert "path" in params, "'path' must be specified for action 'exists'"

        path = params["path"]
        client = s3fs_client()

        start = datetime.now()
        exists = client.exists(path)
        end = datetime.now()

        return ExistsResponse(exists=exists, runtime=int((end - start).microseconds / 1000))
    elif action_type == "put":
        assert "sourcePath" in params, "'sourcePath' must be specified for action 'put'"
        assert (
            "destinationPath" in params
        ), "'destinationPath' must be specified for action 'put'"

        source_path = params["sourcePath"]
        destination_path = params["destinationPath"]
        recursive = params.get("recursive", False)
        client = s3fs_client()

        start = datetime.now()
        client.put(source_path, destination_path, recursive=recursive)
        end = datetime.now()

        return ActionResponse(runtime=int((end - start).microseconds / 1000))
    elif action_type == "get":
        assert "sourcePath" in params, "'sourcePath' must be specified for action 'get'"
        assert (
            "destinationPath" in params
        ), "'destinationPath' must be specified for action 'get'"

        source_path = params["sourcePath"]
        destination_path = params["destinationPath"]
        recursive = params.get("recursive", False)
        client = s3fs_client()

        start = datetime.now()
        client.get(source_path, destination_path, recursive=recursive)
        end = datetime.now()

        return ActionResponse(runtime=int((end - start).microseconds / 1000))
    elif action_type == "rm":
        assert "path" in params, "'path' must be specified for action 'rm'"

        path = params["path"]
        recursive = params.get("recursive", False)
        client = s3fs_client()

        start = datetime.now()
        client.rm(path, recursive=recursive)
        end = datetime.now()

        return ActionResponse(runtime=int((end - start).microseconds / 1000))
    elif action_type == "cb":
        assert "bucketName" in params, "'bucketName' must be specified for action 'cb'"

        bucket_name = params["bucketName"]
        client = boto3_client()

        # TODO: more options
        start = datetime.now()
        client.create_bucket(Bucket=bucket_name)
        end = datetime.now()

        return ActionResponse(runtime=int((end - start).microseconds / 1000))
    elif action_type == "rb":
        assert "bucketName" in params, "'bucketName' must be specified for action 'rb'"

        bucket_name = params["bucketName"]
        client = boto3_client()

        # TODO: more options
        start = datetime.now()
        client.delete_bucket(Bucket=bucket_name)
        end = datetime.now()

        return ActionResponse(runtime=int((end - start).microseconds / 1000))
    else:
        raise ValueError(f"Action type {action_type} is invalid")


def run_assert(assert_type: str, params: AssertParams) -> AssertResult:
    if assert_type == "Exists":
        assert "expected" in params, "'expected' must be specified for assert 'Exists'"
        assert (
            "path" in params or "actionParams" in params
        ), "'path' or 'actionParams' must be specified for assert 'Exists'"

        action_params = params.get("actionParams", {"path": params["path"]})

        action_result: ExistsResponse = run_action("read", action_params)
        passed = action_result["exists"] == params["expected"]

        description = "passed"

        if not passed:
            description = (
                f"expected {params['expected']} but got {action_result['exists']}"
            )

        return AssertResult(
            actual=str(action_result["exists"]),
            expected=params["expected"],
            passed=passed,
            description=description,
        )
    elif assert_type == "ContentsEqual":
        assert (
            "expected" in params
        ), "'expected' must be specified for assert 'ContentsEqual'"
        assert (
            "path" in params or "actionParams" in params
        ), "'path' or 'actionParams' must be specified for assert 'ContentsEqual'"

        action_params = params.get("actionParams", {"path": params["path"]})

        action_result: ReadResponse = run_action("read", action_params)
        passed, description = assert_strings(
            params["expected"], action_result["contents"], match=False
        )

        return AssertResult(
            actual=action_result["contents"],
            expected=params["expected"],
            passed=passed,
            description=description,
        )
    elif assert_type == "ContentsMatch":
        assert (
            "expected" in params
        ), "'expected' must be specified for assert 'ContentsMatch'"
        assert (
            "path" in params or "actionParams" in params
        ), "'path' or 'actionParams' must be specified for assert 'ContentsMatch'"

        action_params = params.get("actionParams", {"path": params["path"]})

        action_result: ReadResponse = run_action("read", action_params)
        passed, description = assert_strings(
            params["expected"], action_result["contents"], match=True
        )

        return AssertResult(
            actual=action_result["contents"],
            expected=params["expected"],
            passed=passed,
            description=description,
        )
    elif assert_type == "FilesEqual":
        assert (
            "expected" in params
        ), "'expected' must be specified for assert 'ContentsMatch'"
        assert (
            "path" in params or "actionParams" in params
        ), "'path' or 'actionParams' must be specified for assert 'FilesEqual'"

        # Use action params if specified, otherwise use provided path
        source_path = params.get("actionParams", {}).get("sourcePath", params["path"])
        destination_path = params.get("actionParams", {}).get(
            "destinationPath", f"/tmp/{uuid4()}"
        )

        action_params = params.get(
            "actionParams",
            {"sourcePath": source_path, "destinationPath": destination_path},
        )

        run_action("get", action_params)
        passed = cmp(params["expected"], destination_path)

        description = "passed"

        if not passed:
            description = (
                f"File contents in {params['expected']} and {source_path} do not match"
            )

        return AssertResult(
            actual=source_path,
            expected=params["expected"],
            passed=passed,
            description=description,
        )
    else:
        raise ValueError(f"Assert type {assert_type} is invalid")
