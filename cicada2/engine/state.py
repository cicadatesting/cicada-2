from typing import Dict, Set, Any, List, Iterable, Union


def combine_keys(dict_a: dict, dict_b: dict) -> Set[str]:
    return set(
        item for sublist in [dict_a.keys(), dict_b.keys()]
        for item in sublist
    )


def combine_data_by_key(combined_outputs: Dict[str, List[Any]], output: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
    combined_keys = combine_keys(combined_outputs, output)

    return {
        key: combine_datas(combined_outputs.get(key, []), output.get(key, []))
        for key in combined_keys
    }


def combine_datas(data_a: Union[List[Any], Any], data_b: Union[List[Any], Any]) -> Union[List[Any], Any]:
    if data_a and data_b:
        # Assert both are lists or not lists
        assert isinstance(data_a, List) == isinstance(data_b, List), (
            f"Cannot combine versioned and non-versioned data: {data_a} + {data_b}"
        )

    # Return list: a and b are non empty lists, a is empty and b is a list, b is empty and a is a list, both are empty
    # Return single item: both are non lists, a is empty and b is not list, b is empty and a is not list
    if (
            (data_a and data_b and not isinstance(data_a, List) and not isinstance(data_b, List))
            or (data_b and not data_a and not isinstance(data_b, List))
    ):
        return data_b
    elif data_a and not data_b and not isinstance(data_a, List):
        return data_a
    else:
        return data_a + data_b


def create_result_name(result_type: str, results: Iterable[str]) -> str:
    name_index = len(
        [name for name in results if name.startswith(result_type)]
    )

    return f"{result_type}{name_index}"
