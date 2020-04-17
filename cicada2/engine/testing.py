import time
import uuid
from collections import defaultdict
from itertools import cycle
from typing import Any, Dict, List

from dask import bag
from dask.distributed import Future, get_client, Variable, wait

from cicada2.engine.actions import run_actions, combine_action_data
from cicada2.engine.asserts import get_remaining_asserts, run_asserts
from cicada2.engine.logs import get_logger
from cicada2.engine.state import combine_data_by_key
from cicada2.engine.types import (
    Action,
    ActionsData,
    Assert,
    Statuses,
    TestSummary
)


LOGGER = get_logger('testing')


def get_default_cycles(actions: List[Action], asserts: List[Assert]) -> int:
    """
    Determine number of default cycles for test given actions and asserts in it

    * If there are asserts, by default run unlimited
    * If there are no asserts but actions, run only once
    * Otherwise, the test has no actions or asserts so do not run

    Args:
        actions: list of actions in test
        asserts: list of asserts in test

    Returns:
        Default number of cycles the test should have
    """
    if asserts:
        return -1
    elif actions:
        return 1

    return 0


def continue_running(
        asserts: List[Assert],
        remaining_cycles: int,
        assert_statuses: Statuses
) -> bool:
    """
    Determines if the test should continue running

    * Stop if no asserts and remaining cycles == 0
    * Stop if has asserts and remaining cycles == 0
    * Stop if has asserts, unlimited cycles, no remaining asserts

    * Keep going if has no remaining asserts and remaining cycles > 0

    Args:
        asserts: List of asserts test has
        remaining_cycles: Number of remaining cycles in test
        assert_statuses: Status of asserts in list

    Returns:
        Whether to continue running or not
    """
    return (
        asserts == [] and remaining_cycles != 0
    ) or (
        asserts != [] and remaining_cycles != 0 and get_remaining_asserts(
            asserts, assert_statuses
        ) != []
    )


def run_actions_parallel(
        actions: List[Action],
        state: defaultdict,
        test_name: str,
        hostnames: List[str],
        seconds_between_actions: float
) -> ActionsData:
    actions_task = bag.from_sequence(
        hostnames
    ).map(
        lambda hostname: run_actions(actions, {**state}, hostname, seconds_between_actions)
    ).fold(
        combine_action_data,
        initial=state[test_name].get('actions', {})
    )

    return actions_task.compute()


def run_asserts_series(
        asserts: List[Assert],
        state: defaultdict,
        test_name: str,
        hostnames: List[str],
        seconds_between_asserts: float
) -> Statuses:
    hostname_asserts_map: Dict[str, List[Assert]] = {}

    for hostname_assert in zip(
            cycle(hostnames),
            get_remaining_asserts(
                asserts,
                state[test_name].get('asserts', {})
            )
    ):
        hostname = hostname_assert[0]
        asrt = hostname_assert[1]

        if hostname not in hostname_asserts_map:
            hostname_asserts_map[hostname] = [asrt]
        else:
            hostname_asserts_map[hostname] += [asrt]

    asserts_task = bag.from_sequence(
        hostname_asserts_map
    ).map(
        lambda h_name: run_asserts(
            hostname_asserts_map[h_name],
            {**state},
            h_name,
            seconds_between_asserts
        )
    ).fold(
        combine_data_by_key,
        initial=state[test_name].get('asserts', {})
    )

    return asserts_task.compute()


def run_test(test_config: dict, incoming_state: dict, hostnames: List[str], timeout_signal_name: str = None):
    actions = test_config.get('actions', [])
    asserts = test_config.get('asserts', [])

    default_cycles = get_default_cycles(actions, asserts)

    remaining_cycles = test_config.get('cycles', default_cycles)
    completed_cycles = 0
    # NOTE: possibly use infinite default dict
    state = defaultdict(dict, incoming_state)

    # Validate tests before running
    # NOTE: may be a good use of walrus operator
    action_names = [a.get('name') for a in actions if a.get('name')]
    assert_names = [a.get('name') for a in asserts if a.get('name')]

    assert hostnames, 'Must have at least one host to run tests'
    assert len(set(action_names)) == len(action_names), 'Action names if specified must be unique'
    assert len(set(assert_names)) == len(assert_names), 'Assert names if specified must be unique'

    for action in actions:
        assert 'type' in action, f"Action in test \'{test_config['name']}\' is missing property 'type'"

    for asrt in asserts:
        assert 'type' in asrt, f"Assert in test \'{test_config['name']}\' is missing property 'type'"

    # stop if remaining_cycles == 0 or had asserts and no asserts remain
    while continue_running(asserts, remaining_cycles, state[test_config['name']].get('asserts', {})):
        # Check if running with a timeout and break if timeout has signaled
        if timeout_signal_name is not None:
            keep_going = Variable(
                timeout_signal_name,
                client=get_client()
            )

            if not keep_going.get():
                break

        # NOTE: exceptions thrown in actions/asserts cause rest of test to exit
        action_distribution_strategy = test_config.get(
            'actionDistributionStrategy', 'parallel'
        )

        # TODO: series distribution strategy
        if action_distribution_strategy == 'parallel' and actions != []:
            state[test_config['name']]['actions'] = run_actions_parallel(
                actions, state, test_config['name'], hostnames, test_config.get('secondsBetweenActions', 0)
            )

        assert_distribution_strategy = test_config.get(
            'assertDistributionStrategy', 'series'
        )

        # TODO: parallel distribution strategy
        if assert_distribution_strategy == 'series' and asserts != []:
            state[test_config['name']]['asserts'] = run_asserts_series(
                asserts,
                state,
                test_config['name'],
                hostnames,
                test_config.get('secondsBetweenAsserts', 0)
            )

        remaining_cycles -= 1
        completed_cycles += 1

        time.sleep(
            test_config.get('secondsBetweenCycles', 1)
        )

    # TODO: just have assert names in remaining asserts
    state[test_config['name']]['summary'] = TestSummary(
        completed_cycles=completed_cycles,
        remaining_asserts=get_remaining_asserts(
            asserts,
            state[test_config['name']].get('asserts', {})
        ),
        error=None
    )

    return state


def run_test_with_timeout(
    test_config,
    incoming_state,
    hostnames,
    duration=15,
    client=None
):
    if duration is None:
        return run_test(test_config, incoming_state, hostnames)

    # NOTE: Use a dask cluster scheduler?
    if client is None:
        client = get_client()

    # NOTE: may improve way of doing this
    timeout_signal_name = f"keep-going-{str(uuid.uuid4())}"
    keep_going = Variable(timeout_signal_name)
    keep_going.set(True)

    run_test_task: Future = client.submit(
        run_test,
        test_config=test_config,
        incoming_state=incoming_state,
        hostnames=hostnames,
        timeout_signal_name=timeout_signal_name
    )

    # NOTE: time.sleep takes no kwargs
    timeout_task: Future = client.submit(lambda: time.sleep(duration))

    # Wait for either test or timeout to finish
    # Return test result if it finishes first
    # End test if timeout finishes first and return state
    wait([run_test_task, timeout_task], return_when='FIRST_COMPLETED')

    if run_test_task.done():
        timeout_task.cancel()
        return run_test_task.result()
    elif timeout_task.done():
        LOGGER.info(f"Test {test_config['name']} timed out")
        # NOTE: add timed out to summary?
        keep_going.set(False)
        return run_test_task.result()
