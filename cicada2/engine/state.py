from typing import Dict, Set, Any, List, Iterable, Union


def combine_keys(dict_a: dict, dict_b: dict) -> Set[str]:
    """
    Combines keys in one dict with keys in another

    # NOTE: maybe get rid of this function as it is a one liner

    Args:
        dict_a: First dictionary to combine keys from
        dict_b: Second dictionary to combine keys from

    Returns:
        Combined keys in both dictionaries
    """
    return set(dict_a).union(dict_b)


def combine_data_by_key(
    combined_outputs: Dict[str, Union[List[Any], Any]],
    output: Dict[str, Union[List[Any], Any]],
) -> Dict[str, Union[List[Any], Any]]:
    """
    Combine lists in two multimaps

    Args:
        combined_outputs: Initial multimap to combine, presumably already combined
        output: New multimap to add to initial multimap

    Returns:
        Combined multimaps (does not modify initial or new data)
    """
    combined_keys = combine_keys(combined_outputs, output)

    return {
        key: combine_datas(combined_outputs.get(key, []), output.get(key, []))
        for key in combined_keys
    }


def combine_datas(
    data_a: Union[List[Any], Any], data_b: Union[List[Any], Any]
) -> Union[List[Any], Any]:
    # pylint: disable=isinstance-second-argument-not-valid-type
    """
    Combines data where either may be versioned (a list) or merged (a single element)

    * Return list: a and b are non empty lists, a is empty and b is a list, b is empty and a is a list, both are empty
    * Return single item: both are non lists, a is empty and b is not list, b is empty and a is not list

    Examples:
        * data_a = [], data_b = 'foo' -> 'foo'
        * data_a = 'foo', data_b = 'bar' -> 'bar'
        * data_a = 'foo', data_b = [] -> 'foo'
        * data_a = ['foo'], data_b = ['bar'] -> ['foo', 'bar']
        * data_a = 'foo', data_b = ['bar'] -> Error, both are non empty but one is versioned and the other is merged

    Args:
        data_a: First data to combine
        data_b: Second data to combine

    Returns:
        Data a and b combined
    """
    if data_a and data_b:
        # Assert both are lists or not lists
        assert isinstance(data_a, List) == isinstance(
            data_b, List
        ), f"Cannot combine versioned and non-versioned data: {data_a} + {data_b}"

    if (
        data_a
        and data_b
        and not isinstance(data_a, List)
        and not isinstance(data_b, List)
    ) or (data_b and not data_a and not isinstance(data_b, List)):
        return data_b
    elif data_a and not data_b and not isinstance(data_a, List):
        return data_a
    else:
        return data_a + data_b


def create_item_name(item_type: str, item_names: Iterable[str]) -> str:
    """
    Translates an item with a type into a name. For instance, if there are two items of type 'POST', the first will
    be named 'POST0' and the second will be 'POST1'

    Args:
        item_type: Type of item
        item_names: Names of current items

    Returns:
        Translated item name
    """
    name_index = len([name for name in item_names if name.startswith(item_type)])

    return f"{item_type}{name_index}"
