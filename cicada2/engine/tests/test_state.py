from cicada2.engine import state


def test_combine_keys():
    dict_a = {'a': 1, 'b': 2}
    dict_b = {'b': 3, 'c': 4}

    combined_keys = state.combine_keys(dict_a, dict_b)

    assert len(combined_keys) == 3
    assert 'a' in combined_keys
    assert 'b' in combined_keys
    assert 'c' in combined_keys


def test_combine_lists_by_key():
    dict_a = {
        'a': [1, 2, 3],
        'b': [4, 5]
    }

    dict_b = {
        'b': [6, 7],
        'c': [8, 9, 10]
    }

    combined_outputs = state.combine_lists_by_key(dict_a, dict_b)

    assert combined_outputs['a'] == [1, 2, 3]
    assert combined_outputs['b'] == [4, 5, 6, 7]
    assert combined_outputs['c'] == [8, 9, 10]


def test_create_result_name():
    result_names = set()

    result_names.add(
        state.create_result_name('A', result_names)
    )

    result_names.add(
        state.create_result_name('A', result_names)
    )

    result_names.add(
        state.create_result_name('B', result_names)
    )

    assert len(result_names) == 3
    assert 'A0' in result_names
    assert 'A1' in result_names
    assert 'B0' in result_names
