from urllib.parse import urlparse
import pytest

from cicada2.operator.io_utility import transfer


def test_get_git_repo():
    url = "git://some-org/some-repo.git"

    parsed_url = urlparse(url)

    repo = transfer.get_git_repo(parsed_url)

    assert repo == ("https://some-org/some-repo.git", "")


def test_get_git_repo_with_protocol():
    url = "git://some-org/some-repo.git?protocol=git"

    parsed_url = urlparse(url)

    assert transfer.get_git_repo(parsed_url) == ("git://some-org/some-repo.git", "")


def test_get_git_repo_invalid_repo():
    url = "git://some-org/some-repo"

    parsed_url = urlparse(url)

    with pytest.raises(AssertionError):
        transfer.get_git_repo(parsed_url)


def test_get_git_repo_invalid_protocol():
    url = "git://some-org/some-repo.git?protocol=xyz"

    parsed_url = urlparse(url)

    with pytest.raises(AssertionError):
        transfer.get_git_repo(parsed_url)


def test_get_git_repo_branch():
    url = "git://some-org/some-repo.git?branch=xyz"

    parsed_url = urlparse(url)

    assert transfer.get_git_repo_branch(parsed_url.query) == "xyz"


def test_get_git_repo_default_branch():
    url = "git://some-org/some-repo.git"

    parsed_url = urlparse(url)

    assert transfer.get_git_repo_branch(parsed_url.query) == "master"
