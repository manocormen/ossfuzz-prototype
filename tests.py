"""Test Modules (naively for now)"""

import pytest

from api import get_project, get_projects, list_projects, match_projects
from models import Project


@pytest.fixture
def dummy_projects():
    """Return a dictionary with a few static projects."""
    return {
        "abseil-cpp": Project(
            name="abseil-cpp",
            language="c++",
            homepage="abseil.io",
            main_repo="https://github.com/abseil/abseil-cpp.git",
            primary_contact="dmauro@google.com",
            vendor_ccs=None,
            fuzzing_engines=None,
            build_system="bazel",
        ),
        "abseil-py": Project(
            name="abseil-py",
            language="python",
            homepage="https://github.com/abseil/abseil-py",
            main_repo="https://github.com/abseil/abseil-py",
            primary_contact=None,
            vendor_ccs=["david@adalogics.com"],
            fuzzing_engines=["libfuzzer"],
            build_system="unknown",
        ),
        "ada-url": Project(
            name="ada-url",
            language="c++",
            homepage="https://ada-url.github.io/ada",
            main_repo="https://github.com/ada-url/ada.git",
            primary_contact="yagiz@nizipli.com",
            vendor_ccs=None,
            fuzzing_engines=["libfuzzer", "afl", "honggfuzz", "centipede"],
            build_system=None,
        ),
    }


def test_list_projects():
    """Naively test function for listing projects (assumes static projects)."""
    observed = list_projects(5)
    expected = ["abseil-cpp", "abseil-py", "ada-url", "adal", "aiohttp"]
    assert observed == expected


def test_get_project(dummy_projects):
    """Naively test function for getting project details (assumes static project)."""
    observed = get_project("ada-url")
    expected = dummy_projects["ada-url"]
    assert observed == expected


def test_get_projects(dummy_projects):
    """Naively test getting details of several projects (assumes static projects)."""
    observed = get_projects(3)
    expected = dummy_projects
    assert observed == expected


def test_match_projects(dummy_projects):
    """Naively test getting projects that match criteria (assumes static projects."""
    observed = match_projects(name="ada", language="c++", fuzzing_engines="afl")
    expected = {"ada-url": dummy_projects["ada-url"]}
    assert observed == expected
