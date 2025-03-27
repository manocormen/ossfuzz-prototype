"""Public module for interacting with OSS-Fuzz projects"""

from collections import defaultdict
from typing import Iterator

import yaml
from dotenv import load_dotenv

from fetch import fetch_project_file, fetch_project_files, fetch_project_names

load_dotenv()

type Project = dict[str, str | list[str]]
type Projects = dict[str, Project]

BATCH_SIZE = 100

_projects_cache: Projects = {}


def list_projects(limit: int | None = None) -> list[str]:
    """Return the names of projects, up to limit."""
    projects = fetch_project_names()
    return projects if limit is None else projects[:limit]


def get_project_details(project_name: str) -> Project:
    """Return the details of a specific OSS-Fuzz project."""
    project_yaml = yaml.safe_load(fetch_project_file(project_name, "project.yaml"))
    build_sh = fetch_project_file(project_name, "build.sh")
    project_details = {
        "name": project_name,
        "language": project_yaml.get("language"),
        "homepage": project_yaml.get("homepage"),
        "main_repo": project_yaml.get("main_repo"),
        "primary_contact": project_yaml.get("primary_contact"),
        "vendor_ccs": project_yaml.get("vendor_ccs", []),
        "fuzzing_engines": project_yaml.get("fuzzing_engines", []),
        "build_system": _infer_build_system(build_sh),
    }
    return project_details


def cache_all_projects() -> None:
    """Fetch and cache select data for all OSS-Fuzz projects (in batches)."""
    project_yaml_files, build_sh_files = {}, {}
    print("Please wait: caching project data... (just once)")
    for pnames in _batch_list(list_projects(), BATCH_SIZE):
        project_yaml_files.update(fetch_project_files(pnames, "project.yaml"))
        build_sh_files.update(fetch_project_files(pnames, "build.sh"))
    global _projects_cache
    _projects_cache = _merge_by_project(project_yaml_files, build_sh_files)


def _infer_build_system(file: str) -> str | None:
    """Heuristically infer the build system using in a file."""
    file = file.lower()
    if "cmake" in file:
        return "cmake"
    if "make" in file:
        return "make"
    if "ninja" in file:
        return "ninja"
    if "bazel" in file:
        return "bazel"
    return None


def _merge_by_project(projects1: Projects, projects2: Projects) -> Projects:
    """Merge two dictionaries of projects into one, keyed by project names."""
    merged_projects: Projects = defaultdict(dict)
    for pname in projects1:
        merged_projects[pname].update(projects1[pname] or {})
        merged_projects[pname].update(projects2[pname] or {})
    return dict(merged_projects)


def _batch_list(list_: list, batch_size: int) -> Iterator[list]:
    """Break input list into batches."""
    for i in range(0, len(list_), batch_size):
        yield list_[i : i + batch_size]
