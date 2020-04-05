from typing import Dict, Set, Any, List, Iterable


def combine_keys(dict_a: dict, dict_b: dict) -> Set[str]:
    return set(
        item for sublist in [dict_a.keys(), dict_b.keys()]
        for item in sublist
    )


def combine_lists_by_key(combined_outputs: Dict[str, List[Any]], output: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
    combined_keys = combine_keys(combined_outputs, output)

    # TODO: support combining non-list outputs (non-versioned)
    return {
        key: combined_outputs.get(key, []) + output.get(key, [])
        for key in combined_keys
    }


def create_result_name(result_type: str, results: Iterable[str]) -> str:
    name_index = len(
        [name for name in results if name.startswith(result_type)]
    )

    return f"{result_type}{name_index}"
