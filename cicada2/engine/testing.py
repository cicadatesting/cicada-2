import traceback
from collections import defaultdict
from itertools import cycle
from typing import Any, Dict, List

from dask import bag
from dask.distributed import Client, TimeoutError, wait

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

    print(hostname_asserts_map)

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


def run_test(test_config: dict, incoming_state: dict, hostnames: List[str]):
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

        remaining_cycles -= 1

    # TODO: test result reporting
    # TODO: what to return if test finishes with remaining asserts?
    return state


def run_test_with_timeout(
    test_config,
    incoming_state,
    hostnames,
    duration=15,
    timeout_allowed=False,
    client=None
):
    if duration is None:
        return run_test(test_config, incoming_state, hostnames)

    try:
        # NOTE: is nested client a good idea?
        if client is None:
            client = Client(processes=False)

        task = client.submit(
            lambda: run_test(test_config, incoming_state, hostnames)
        )

        wait([task], timeout=duration)

        # TODO: traceback in debug logs
        tb = task.traceback()

        if tb is not None:
            print(traceback.format_tb(tb))

        return task.result()
    except TimeoutError:
        # TODO: more descriptive failed test reporting
        print(f"Test {test_config['name']} timed out")

        if timeout_allowed:
            return incoming_state
        else:
            return None
