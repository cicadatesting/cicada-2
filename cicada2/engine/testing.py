import traceback
import time
import uuid
from collections import defaultdict
from itertools import cycle
from typing import Any, Dict, List

from dask import bag
from dask.distributed import Future, get_client, Variable

from cicada2.engine.actions import run_actions, combine_action_data, Action, ActionsData
from cicada2.engine.asserts import get_remaining_asserts, run_asserts, Assert, Statuses
from cicada2.engine.state import combine_lists_by_key


def get_default_cycles(actions: List[Any], asserts: List[Any]) -> int:
    if asserts:
        return -1
    elif actions:
        return 1

    return 0


def continue_running(
        asserts: List[Any],
        remaining_cycles: int,
        assert_statuses: Statuses
) -> bool:
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
        hostnames: List[str]
) -> ActionsData:
    actions_task = bag.from_sequence(
        hostnames
    ).map(
        lambda hostname: run_actions(actions, {**state}, hostname)
    ).fold(
        combine_action_data,
        initial=state[test_name].get('actions', {})
    )

    return actions_task.compute()


def run_asserts_series(
        asserts: List[Assert],
        state: defaultdict,
        test_name: str,
        hostnames: List[str]
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
            h_name
        )
    ).fold(
        combine_lists_by_key,
        initial=state[test_name].get('asserts', {})
    )

    return asserts_task.compute()


def run_test(test_config: dict, incoming_state: dict, hostnames: List[str], timeout_signal_name: str = None):
    actions = test_config.get('actions', [])
    asserts = test_config.get('asserts', [])

    default_cycles = get_default_cycles(actions, asserts)

    remaining_cycles = test_config.get('cycles', default_cycles)
    # NOTE: possibly use infinite default dict
    state = defaultdict(dict, incoming_state)

    # TODO: ensure at least one hostname
    # TODO: ensure action/assert names unique if specified

    # stop if remaining_cycles == 0 or had asserts and no asserts remain
    while continue_running(asserts, remaining_cycles, state[test_config['name']].get('asserts', {})):
        if timeout_signal_name is not None:
            keep_going = Variable(timeout_signal_name)

            if not keep_going.get():
                return state

        action_distribution_strategy = test_config.get(
            'actionDistributionStrategy', 'parallel'
        )

        # TODO: series distribution strategy
        if action_distribution_strategy == 'parallel' and actions != []:
            # TODO: make sure test_config['name'] exists in validation
            state[test_config['name']]['actions'] = run_actions_parallel(
                actions, state, test_config['name'], hostnames
            )

        assert_distribution_strategy = test_config.get(
            'assertDistributionStrategy', 'series'
        )

        # TODO: parallel distribution strategy
        if assert_distribution_strategy == 'series' and asserts != []:
            state[test_config['name']]['asserts'] = run_asserts_series(asserts, state, test_config['name'], hostnames)

        # TODO: report total cycles, remaining cycles
        remaining_cycles -= 1

        # TODO: configurable sleep between cycles
        time.sleep(1)

    # TODO: test result reporting
    # TODO: what to return if test finishes with remaining asserts?
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
    timeout_signal_name = f"keep-going-{str(uuid.uuid4())[:8]}"
    keep_going = Variable(timeout_signal_name)
    keep_going.set(True)

    run_test_task: Future = client.submit(
        run_test,
        test_config=test_config,
        incoming_state=incoming_state,
        hostnames=hostnames,
        timeout_signal_name=timeout_signal_name
    )

    # time.sleep takes no kwargs
    timeout_task: Future = client.submit(lambda: time.sleep(duration))

    # Wait for either test or timeout to finish
    # Return test result if it finishes first
    # End test if timeout finishes first and return state
    while True:
        if run_test_task.done():
            return run_test_task.result()
        elif timeout_task.done():
            print(f"Test {test_config['name']} timed out")
            # TODO: set somewhere that test succeed/failed
            keep_going.set(False)
            return run_test_task.result()

        # tb = run_test_task.traceback()
        #
        # if tb is not None:
        #     # TODO: traceback in debug logs
        #     print(traceback.format_tb(tb))
        #     run_test_task.cancel()
        #     timeout_task.cancel()

        # NOTE: possibly sleep between polls
