import os
import shutil
import uuid
from urllib.parse import urlparse, parse_qs

import git
from s3fs import S3FileSystem

from cicada2.operator.io_utility.config import (
    S3_ENDPOINT,
    S3_REGION,
    S3_ACCESS_KEY_ID,
    S3_SECRET_ACCESS_KEY,
    S3_SESSION_TOKEN,
    USE_SSL,
)


def transfer_files(src: str, dest: str):
    src_parsed = urlparse(src)
    dest_parsed = urlparse(dest)

    # TODO: save already cloned repo
    # TODO: file to file transfers
    # NOTE: maybe move to seperate functions

    if src_parsed.scheme == "s3" and dest_parsed.scheme == "file":
        assert os.path.exists(src), f"{src} not found"

        client = s3fs_client()
        client.get(src, dest_parsed.path, recursive=True)
    elif src_parsed.scheme == "file" and dest_parsed.scheme == "s3":
        assert os.path.exists(src_parsed.path), f"{src_parsed.path} not found"

        client = s3fs_client()
        client.put(src_parsed.path, dest, recursive=True)
    elif src_parsed.scheme == "git" and dest_parsed.scheme == "file":
        repo_dir = os.path.join("/tmp", str(uuid.uuid4())[:8])
        repo_url, subpath = get_git_repo(src_parsed)
        branch = get_git_repo_branch(src_parsed.query)

        download_git_repo(repo_url, repo_dir, branch)
        src_path = os.path.join(repo_dir, subpath)

        assert os.path.exists(src_path), f"{src_path} not found"

        if os.path.isdir(src_path):
            copydir(src_path, dest_parsed.path)
        elif os.path.isfile(src_path):
            shutil.copy2(src_path, dest_parsed.path)
        else:
            raise RuntimeError("File not found in git repo: {subpath}")
    else:
        raise RuntimeError(f"Unsupported transfer: {src} to {dest}")


def s3fs_client() -> S3FileSystem:
    return S3FileSystem(
        key=S3_ACCESS_KEY_ID,
        secret=S3_SECRET_ACCESS_KEY,
        token=S3_SESSION_TOKEN,
        use_ssl=USE_SSL,
        client_kwargs={"endpoint_url": S3_ENDPOINT, "region_name": S3_REGION},
    )


def get_git_repo(parsed_url):
    protocol = get_git_repo_protocol(parsed_url.query)
    path_parts = parsed_url.path.split(".git")

    assert protocol in [
        "http",
        "https",
        "ftp",
        "ftps",
        "git",
        "ssh",
    ], "Invalid git download protocol"
    assert len(path_parts) >= 2, "Remote git path must contain '.git'"

    return (
        f"{protocol}://{parsed_url.netloc}{path_parts[0]}.git",
        path_parts[1].strip("/"),
    )


def get_git_repo_protocol(querystring):
    parsed_querystring = parse_qs(querystring)

    if "protocol" in parsed_querystring and len(parsed_querystring["protocol"]) > 0:
        return parsed_querystring["protocol"][0]

    return "https"


def get_git_repo_branch(querystring):
    parsed_querystring = parse_qs(querystring)

    if "branch" in parsed_querystring and len(parsed_querystring["branch"]) > 0:
        return parsed_querystring["branch"][0]

    # TODO: change to 'main' when enacted
    return "master"


def download_git_repo(repo_url, temp_dir, branch="master"):
    git.Repo.clone_from(repo_url, temp_dir, branch=branch)

    return temp_dir


def copydir(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copydir(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
