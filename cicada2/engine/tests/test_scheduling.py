from unittest.mock import Mock

from cicada2.engine import scheduling


def test_sort_dependencies():
    dependency_map = {"A": ["B"], "B": [], "C": ["A"], "D": ["B"], "E": ["A", "C"]}

    sorted_dependencies = scheduling.sort_dependencies(dependency_map)

    assert len(sorted_dependencies) == 5
    assert sorted_dependencies[0] == "B"
    assert sorted_dependencies[1] in ["A", "D"]
    assert sorted_dependencies[2] in ["A", "D", "C"]
    assert sorted_dependencies[3] in ["C", "D"]
    assert sorted_dependencies[4] == "E"


def test_test_is_ready_no_dependencies():
    dependency_map = {"A": []}

    assert scheduling.test_is_ready(
        test_name="A", test_statuses={"A": None}, test_dependencies=dependency_map
    )


def test_test_is_ready_already_running():
    dependency_map = {"A": []}

    assert not scheduling.test_is_ready(
        test_name="A", test_statuses={"A": True}, test_dependencies=dependency_map
    )


def test_test_is_ready_with_dependencies():
    dependency_map = {"A": [], "B": ["A"]}

    mock_a = Mock()
    mock_done = Mock()

    mock_a.done = mock_done
    mock_a.done.return_value = True

    test_statuses = {"A": mock_a, "B": None}

    assert scheduling.test_is_ready(
        test_name="B", test_statuses=test_statuses, test_dependencies=dependency_map
    )


def test_test_is_ready_dependency_running():
    dependency_map = {"A": [], "B": ["A"]}

    mock_a = Mock()
    mock_done = Mock()

    mock_a.done = mock_done
    mock_a.done.return_value = False

    test_statuses = {"A": mock_a, "B": None}

    assert not scheduling.test_is_ready(
        test_name="B", test_statuses=test_statuses, test_dependencies=dependency_map
    )


def test_all_tests_finished_empty():
    test_statuses = {"A": None, "B": None}

    assert not scheduling.all_tests_finished(test_statuses)


def test_all_tests_finished_one_in_progress():
    mock_a = Mock()
    mock_a_done = Mock()

    mock_a.done = mock_a_done
    mock_a.done.return_value = True

    mock_b = Mock()
    mock_b_done = Mock()

    mock_b.done = mock_b_done
    mock_b.done.return_value = False

    test_statuses = {"A": mock_a, "B": mock_b}

    assert not scheduling.all_tests_finished(test_statuses)


def test_all_tests_finished_both_done():
    mock_a = Mock()
    mock_a_done = Mock()

    mock_a.done = mock_a_done
    mock_a.done.return_value = True

    mock_b = Mock()
    mock_b_done = Mock()

    mock_b.done = mock_b_done
    mock_b.done.return_value = True

    test_statuses = {"A": mock_a, "B": mock_b}

    assert scheduling.all_tests_finished(test_statuses)
