import sys

from cicada2.engine.scheduling import run_tests
from cicada2.engine.config import EXIT_CODE_OVERRIDE


def main():
    # NOTE: inverted result of run_tests because False becomes 0, we want 1
    # if result is false
    all_tests_succeeded = run_tests()

    if EXIT_CODE_OVERRIDE:
        exit_code = int(EXIT_CODE_OVERRIDE)
    elif not all_tests_succeeded:
        exit_code = 1
    else:
        exit_code = 0

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
