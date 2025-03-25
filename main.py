"""OSS-Fuzz-Research"""

import base64
import os
from collections import defaultdict
from typing import Iterator

import httpx
import yaml
from dotenv import load_dotenv

load_dotenv()

type Project = dict[str, str | list[str]]
type Projects = dict[str, Project]

BASE_URL = "https://api.github.com"
CONTENTS_ENDPOINT = "/repos/google/oss-fuzz/contents"
GRAPHQL_ENDPOINT = "/graphql"

BATCH_SIZE = 100

_projects_cache: Projects = {}


def list_projects(limit: int | None = None) -> list[str]:
    """Return the names of OSS-Fuzz projects, up to limit."""
    response = httpx.get(BASE_URL + CONTENTS_ENDPOINT + "/projects")
    projects = [project["name"] for project in response.json()]
    return projects if limit is None else projects[:limit]


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


def _fetch_project_file(project_name: str, filename: str) -> str:
    """Fetch specific file for given OSS-Fuzz projects via GitHub's REST API."""
    url = BASE_URL + CONTENTS_ENDPOINT + f"/projects/{project_name}/{filename}"
    response = httpx.get(url)
    file = base64.b64decode(response.json().get("content", "")).decode()
    return file


def get_project_details(project_name: str) -> Project:
    """Return the details of a specific OSS-Fuzz project."""
    project_yaml = yaml.safe_load(_fetch_project_file(project_name, "project.yaml"))
    build_sh = _fetch_project_file(project_name, "build.sh")
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


def _sanitize_identifier(identifier: str) -> str:
    """Replace invalid characters in identifier with underscores."""
    return identifier.replace(".", "_").replace("-", "_")


def _fetch_project_files_query(project_names: list[str], filename: str) -> str:
    """Return query for fetching project files in bulk via GitHub's GraphQL API."""
    inner_fragment = "\n".join(
        [
            f"""
                {_sanitize_identifier(pname)}: object(expression: "HEAD:projects/{pname}/{filename}") {{
                    ... on Blob {{
                        {_sanitize_identifier(filename)}: text
                    }}
                }}
            """
            for pname in project_names
        ]
    )
    query = f"""
        {{
            repository(owner: "google", name: "oss-fuzz") {{
                {inner_fragment}
            }}
        }}
    """
    return query


def _merge_by_project(projects1: Projects, projects2: Projects) -> Projects:
    """Merge two dictionaries of projects into one, keyed by project names."""
    merged_projects: Projects = defaultdict(dict)
    for pname in projects1:
        merged_projects[pname].update(projects1[pname] or {})
        merged_projects[pname].update(projects2[pname] or {})
    return dict(merged_projects)


def _fetch_project_files(project_names: list[str], filename: str) -> Projects:
    """Fetch specific file for given OSS-Fuzz projects via GitHub's GraphQL API."""
    headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
    payload = {"query": _fetch_project_files_query(project_names, filename)}
    response = httpx.post(
        BASE_URL + GRAPHQL_ENDPOINT, headers=headers, json=payload, timeout=30
    )
    projects = response.json()["data"]["repository"]
    return projects


def _batch_list(list_: list, batch_size: int) -> Iterator[list]:
    """Break input list into batches."""
    for i in range(0, len(list_), batch_size):
        yield list_[i : i + batch_size]


def cache_all_projects() -> None:
    """Fetch and cache select data for all OSS-Fuzz projects (in batches)."""
    project_yaml_files, build_sh_files = {}, {}
    print("Please wait: caching project data... (just once)")
    for pnames in _batch_list(list_projects(), BATCH_SIZE):
        project_yaml_files.update(_fetch_project_files(pnames, "project.yaml"))
        build_sh_files.update(_fetch_project_files(pnames, "build.sh"))
    global _projects_cache
    _projects_cache = _merge_by_project(project_yaml_files, build_sh_files)
