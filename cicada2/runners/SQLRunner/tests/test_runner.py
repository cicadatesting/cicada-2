from cicada2.runners.SQLRunner import runner


def test_contains_rows():
    expected_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        },
        {
            'foo': 'alpha',
            'fizz': 'bravo'
        }
    ]

    actual_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        },
        {
            'foo': 'alpha',
            'fizz': 'bravo'
        }
    ]

    passed, description = runner.contains_rows(expected_rows, actual_rows)

    assert passed
    assert description == 'passed'


def test_contains_rows_subset_1():
    expected_rows = [
        {
            'foo': 'bar'
        },
        {
            'foo': 'alpha'
        }
    ]

    actual_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        },
        {
            'foo': 'alpha',
            'fizz': 'bravo'
        }
    ]

    passed, description = runner.contains_rows(expected_rows, actual_rows)

    assert passed
    assert description == 'passed'


def test_contains_rows_subset_2():
    expected_rows = [
        {
            'foo': 'bar'
        },
        {
            'foo': 'alpha'
        }
    ]

    actual_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        },
        {
            'foo': 'alpha',
            'fizz': 'bravo'
        },
        {
            'foo': 1,
            'fizz': 2
        }
    ]

    passed, description = runner.contains_rows(expected_rows, actual_rows)

    assert passed
    assert description == 'passed'


def test_contains_rows_fail_1():
    expected_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        },
        {
            'foo': 'alpha',
            'fizz': 'bravo'
        }
    ]

    actual_rows = [
        {
            'foo': 'bar'
        },
        {
            'foo': 'alpha'
        }
    ]

    passed, description = runner.contains_rows(expected_rows, actual_rows)

    assert not passed


def test_contains_rows_fail_2():
    expected_rows = [
        {
            'foo': 'bar'
        },
        {
            'foo': 'alpha'
        },
        {
            'foo': 1
        }
    ]

    actual_rows = [
        {
            'foo': 'bar'
        },
        {
            'foo': 'alpha'
        }
    ]

    passed, description = runner.contains_rows(expected_rows, actual_rows)

    assert not passed
    assert description == "The following rows did not match any returned: [{'foo': 1}]"


def test_equals_rows():
    expected_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        },
        {
            'foo': 'alpha',
            'fizz': 'bravo'
        }
    ]

    actual_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        },
        {
            'foo': 'alpha',
            'fizz': 'bravo'
        }
    ]

    passed, description = runner.equals_rows(expected_rows, actual_rows)

    assert passed
    assert description == 'passed'


def test_equals_rows_different_length_1():
    expected_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        }
    ]

    actual_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        },
        {
            'foo': 'alpha',
            'fizz': 'bravo'
        }
    ]

    passed, description = runner.equals_rows(expected_rows, actual_rows)

    assert not passed
    assert description == 'Expected 1 rows, got 2'


def test_equals_rows_different_length_2():
    expected_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        },
        {
            'foo': 'alpha',
            'fizz': 'bravo'
        }
    ]

    actual_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        }
    ]

    passed, description = runner.equals_rows(expected_rows, actual_rows)

    assert not passed
    assert description == 'Expected 2 rows, got 1'


def test_equals_rows_failed():
    expected_rows = [
        {
            'foo': 'alpha',
            'fizz': 'bravo'
        }
    ]

    actual_rows = [
        {
            'foo': 'bar',
            'fizz': 'buzz'
        }
    ]

    passed, description = runner.equals_rows(expected_rows, actual_rows)

    assert not passed
    assert description == "Expected {'foo': 'alpha', 'fizz': 'bravo'}, got {'foo': 'bar', 'fizz': 'buzz'}"
