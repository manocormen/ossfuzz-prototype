"""Interact with API"""

from collections import defaultdict

import yaml
from dotenv import load_dotenv

from fetch import fetch_project_file, fetch_project_files, fetch_project_names
from models import Project

load_dotenv()


BATCH_SIZE = 100

_projects_cache = {}


def list_projects(limit: int | None = None) -> list[str]:
    """Return the names of projects, up to limit."""
    projects = fetch_project_names()
    return projects if limit is None else projects[:limit]


def get_project(project_name: str) -> Project:
    """Return the details of a specific project."""
    project_yaml = yaml.safe_load(fetch_project_file(project_name, "project.yaml"))
    build_sh = fetch_project_file(project_name, "build.sh")
    project = Project(
        name=project_name,
        language=project_yaml.get("language"),
        homepage=project_yaml.get("homepage"),
        main_repo=project_yaml.get("main_repo"),
        primary_contact=project_yaml.get("primary_contact"),
        vendor_ccs=project_yaml.get("vendor_ccs"),
        fuzzing_engines=project_yaml.get("fuzzing_engines"),
        build_system=_infer_build_system(build_sh),
    )
    return project


def cache_projects(limit: int | None = None) -> None:
    """Cache the projects, up to limit."""
    print("Please wait: caching project data... (just once)")
    project_yaml_files = fetch_project_files(list_projects(limit), "project.yaml")
    build_sh_files = fetch_project_files(list_projects(limit), "build.sh")
    projects = {}
    for project_name in project_yaml_files:
        project_yaml = yaml.safe_load(project_yaml_files[project_name])
        build_sh = build_sh_files[project_name]
        projects[project_name] = Project(
            name=project_name,
            language=project_yaml.get("language"),
            homepage=project_yaml.get("homepage"),
            main_repo=project_yaml.get("main_repo"),
            primary_contact=project_yaml.get("primary_contact"),
            vendor_ccs=project_yaml.get("vendor_ccs"),
            fuzzing_engines=project_yaml.get("fuzzing_engines"),
            build_system=_infer_build_system(build_sh) if build_sh else None,
        )
    global _projects_cache
    _projects_cache = projects


def _infer_build_system(file: str) -> str:
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
    return ""


def _merge_by_project(projects1: dict, projects2: dict) -> dict:
    """Merge two dictionaries of projects into one, keyed by project names."""
    merged_projects: defaultdict = defaultdict(dict)
    for pname in projects1:
        merged_projects[pname].update(projects1[pname] or {})
        merged_projects[pname].update(projects2[pname] or {})
    return dict(merged_projects)
