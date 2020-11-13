import sys

from cicada2.engine.scheduling import run_tests
from cicada2.engine.config import EXIT_CODE_OVERRIDE


if __name__ == "__main__":
    # NOTE: inverted result of run_tests because False becomes 0, we want 1
    # if result is false
    exit_code = int(not run_tests())

    if EXIT_CODE_OVERRIDE:
        sys.exit(int(EXIT_CODE_OVERRIDE))

    sys.exit(exit_code)
