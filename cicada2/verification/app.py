# load state file (default to state.final.json)
# Determine if all tests passed or failed
# exit code accordingly (with logging)
from urllib.parse import urlparse
from os import getenv
from datetime import datetime, timedelta
import sys
import json
import time

from s3fs import S3FileSystem
import click

from cicada2.engine.reporting import test_succeeded
from cicada2.shared.logs import get_logger

LOGGER = get_logger("verification")


def s3fs_client() -> S3FileSystem:
    return S3FileSystem(
        key=getenv("S3_ACCESS_KEY_ID"),
        secret=getenv("S3_SECRET_ACCESS_KEY"),
        token=getenv("S3_SESSION_TOKEN"),
        use_ssl=getenv("USE_SSL", "true").lower() in ["true", "t", "y", "yes"],
        client_kwargs={
            "endpoint_url": getenv("S3_ENDPOINT"),
            "region_name": getenv("S3_REGION"),
        },
        skip_instance_cache=True,
    )


def read_with_timeout(wait_time: int, read_fn):
    end_time = datetime.now() + timedelta(seconds=wait_time)

    while datetime.now() < end_time:
        try:
            return read_fn()
        except FileNotFoundError:
            LOGGER.info("File not found, retrying in 5 seconds...")
            time.sleep(5)

    raise FileNotFoundError("Timed out waiting for file to become available")


# pylint: disable=no-value-for-parameter
@click.command()
@click.option(
    "--state-file",
    default="file:///input/state.final.json",
    help="State file to verify",
)
@click.option(
    "--timeout",
    default=120,
    help="Time to wait for file to become available",
)
def verify_tests(state_file: str, timeout: int) -> bool:
    parsed_state_file_path = urlparse(state_file)

    if parsed_state_file_path.scheme == "file":
        LOGGER.debug("Loading file %s from local", parsed_state_file_path.path)

        def read_fn():
            with open(parsed_state_file_path.path) as state_fp:
                return json.load(state_fp)

        state_file_contents = read_with_timeout(timeout, read_fn)
    elif parsed_state_file_path.scheme == "s3":
        LOGGER.debug("Loading file %s from s3", state_file)
        client = s3fs_client()

        def read_fn():
            # s3fs will cache bucket location info (which we expect to change while waiting)
            client.invalidate_cache()
            with client.open(state_file, "r") as state_fp:
                return json.load(state_fp)

        state_file_contents = read_with_timeout(timeout, read_fn)
    else:
        raise ValueError(f"scheme '{parsed_state_file_path.scheme}' invalid")

    all_tests_succeeded = True

    for test_name, test_results in state_file_contents.items():
        if "summary" in test_results:
            summary = test_results["summary"]

            succeeded = test_succeeded(summary)

            LOGGER.info(
                "Test %s: %s",
                test_name,
                ("succeeded" if succeeded else "failed"),
            )

            all_tests_succeeded &= succeeded

    return all_tests_succeeded


def main():
    all_tests_succeeded = verify_tests()

    if not all_tests_succeeded:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
