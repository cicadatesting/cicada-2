# load state file (default to state.final.json)
# Determine if all tests passed or failed
# exit code accordingly (with logging)
import sys
import json

import click

from cicada2.engine.reporting import test_succeeded
from cicada2.shared.logs import get_logger

LOGGER = get_logger("verification")


@click.command()
@click.option(
    "--state-file", default="/input/state.final.json", help="State file to verify"
)
def verify_tests(state_file):
    with open(state_file) as state_fp:
        state_file_contents = json.load(state_fp)
        all_tests_succeeded = True

        for test_name, test_results in state_file_contents.items():
            if "summary" in test_results:
                summary = test_results["summary"]

                succeeded = test_succeeded(summary)

                LOGGER.info(
                    "Test %s: %s", test_name, ("succeeded" if succeeded else "failed")
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
