from cicada2.shared import asserts, types


def test_assert_dicts_equal():
    expected = {"foo": "bar"}
    actual = {"foo": "bar"}

    passed, _ = asserts.assert_dicts(expected, actual, all_required=True)

    assert passed


def test_assert_dicts_contains():
    expected = {"foo": "bar"}
    actual = {"foo": "bar", "fizz": "buzz"}

    passed, _ = asserts.assert_dicts(expected, actual)

    assert passed


def test_assert_dicts_not_equals():
    expected = {"foo": "bar"}
    actual = {"fizz": "buzz"}

    passed, _ = asserts.assert_dicts(expected, actual)

    assert not passed


def test_assert_dicts_not_contains():
    expected = {"foo": "bar", "fizz": "buzz"}
    actual = {"foo": "bar"}

    passed, _ = asserts.assert_dicts(expected, actual)

    assert not passed


def test_assert_dicts_nested_dicts():
    expected = {"foo": "bar", "fizz": {"foo": "bar"}}
    actual = {"foo": "bar", "fizz": {"foo": "bar", "fizz": "buzz"}}

    passed, _ = asserts.assert_dicts(expected, actual)

    assert passed


def test_assert_strings_equal():
    expected = "foo"
    actual = "foo"

    passed, _ = asserts.assert_strings(expected, actual, match=False)

    assert passed


def test_assert_strings_not_equal():
    expected = "foo"
    actual = "bar"

    passed, _ = asserts.assert_strings(expected, actual, match=False)

    assert not passed


def test_assert_strings_match():
    expected = "^[a-zA-Z0-9_-]+$"
    actual = "foo-bar"

    passed, _ = asserts.assert_strings(expected, actual, match=True)

    assert passed


def test_assert_strings_not_match():
    expected = "^[a-zA-Z0-9_-]+$"
    actual = "foo bar"

    passed, _ = asserts.assert_strings(expected, actual, match=True)

    assert not passed


def test_assert_collections_unordered():
    expected = [1, 2, 3]
    actual = [3, 2, 1]

    passed, _ = asserts.assert_collections(expected, actual)

    assert passed


def test_assert_collections_ordered():
    expected = [1, 2, 3]
    actual = [3, 2, 1]

    passed, _ = asserts.assert_collections(expected, actual, ordered=True)

    assert not passed


def test_assert_collections_contains():
    expected = [1, 2, 3]
    actual = [3, 2, 1, 4]

    passed, _ = asserts.assert_collections(expected, actual)

    assert passed


def test_assert_collections_same_size():
    expected = [1, 2, 3]
    actual = [3, 2, 1, 4]

    passed, _ = asserts.assert_collections(expected, actual, all_required=True)

    assert not passed


def test_assert_collections_nested():
    expected = [1, [2, 3]]
    actual = [[3, 2], 1, 4]

    passed, _ = asserts.assert_collections(expected, actual)

    assert passed


def test_assert_element_both_none():
    expected = None
    actual = None

    passed, _ = asserts.assert_element(expected, actual)

    assert passed


def test_assert_element_expected_none():
    expected = None
    actual = "foo"

    passed, _ = asserts.assert_element(expected, actual)

    assert not passed


def test_assert_element_nested():
    expected = {"foo": {"fizz": [3, 1, 2], "buzz": "^[a-zA-Z0-9_-]+$"}, "bar": True}
    actual = {
        "foo": {"fizz": [3, 1, 2, 4], "buzz": "fizz-buzz"},
        "bar": True,
        "bar2": False,
    }

    passed, _ = asserts.assert_element(expected, actual, match=True)

    assert passed


def test_get_remaining_asserts():
    test_asserts = [
        {"name": "A"},
        {"type": "B", "name": "B0"},
        {"type": "B", "name": "B1"},
        {"type": "C", "name": "C0"},
    ]

    statuses = {
        "A": [
            types.AssertResult(passed=False, actual="", expected="", description=""),
            types.AssertResult(passed=True, actual="", expected="", description=""),
        ],
        "B0": [
            types.AssertResult(passed=True, actual="", expected="", description=""),
            types.AssertResult(passed=True, actual="", expected="", description=""),
        ],
        "B1": [
            types.AssertResult(passed=False, actual="", expected="", description=""),
            types.AssertResult(passed=False, actual="", expected="", description=""),
        ],
        "C0": [
            types.AssertResult(passed=False, actual="", expected="", description="")
        ],
    }

    remaining_asserts = asserts.get_remaining_asserts(test_asserts, statuses)

    assert len(remaining_asserts) == 2
    assert {"type": "B", "name": "B1"} in remaining_asserts
    assert {"type": "C", "name": "C0"} in remaining_asserts


def test_get_remaining_asserts_unversioned():
    test_asserts = [
        {"name": "A"},
        {"type": "B", "name": "B0"},
        {"type": "B", "name": "B1"},
        {"type": "C", "name": "C0"},
    ]

    statuses = {
        "A": types.AssertResult(passed=True, actual="", expected="", description=""),
        "B0": types.AssertResult(passed=True, actual="", expected="", description=""),
        "B1": types.AssertResult(passed=False, actual="", expected="", description=""),
        "C0": types.AssertResult(passed=False, actual="", expected="", description=""),
    }

    remaining_asserts = asserts.get_remaining_asserts(test_asserts, statuses)

    assert len(remaining_asserts) == 2
    assert {"type": "B", "name": "B1"} in remaining_asserts
    assert {"type": "C", "name": "C0"} in remaining_asserts


def test_get_remaining_asserts_no_status():
    test_asserts = [
        {"name": "A"},
        {"type": "B"},
        {"type": "B"},
        {
            "type": "C",
        },
    ]

    remaining_asserts = asserts.get_remaining_asserts(test_asserts, {})

    assert remaining_asserts == test_asserts
