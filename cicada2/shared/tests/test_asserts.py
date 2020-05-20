from cicada2.shared import asserts


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
