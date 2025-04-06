"""Fetch Data"""

import base64
import os

import httpx

from loader import load_projects_from_local_file
from utils import batch_list, sanitize

BASE_URL = "https://api.github.com"
CONTENTS_ENDPOINT = "/repos/google/oss-fuzz/contents"
GRAPHQL_ENDPOINT = "/graphql"


def fetch_project_names() -> list[str]:
    """Fetch the names of all projects via GitHub's REST API."""
    try:
        response = httpx.get(BASE_URL + CONTENTS_ENDPOINT + "/projects")
        response.raise_for_status()
        projects = [project["name"] for project in response.json()]
    except httpx.HTTPError:  # Rough fallback, to allow demo to proceed if API fails
        projects = list(load_projects_from_local_file("fallback.json").keys())
    return projects


def fetch_project_file(project_name: str, filename: str) -> str | None:
    """Fetch file for specific project via GitHub's REST API."""
    try:
        url = BASE_URL + CONTENTS_ENDPOINT + f"/projects/{project_name}/{filename}"
        response = httpx.get(url).raise_for_status()
        file_content = base64.b64decode(response.json().get("content", "")).decode()
    except httpx.HTTPError:  # Rough fallback, to allow demo to proceed if API fails
        project = load_projects_from_local_file("fallback.json")[project_name]
        file_content = getattr(project, sanitize(filename))
    return file_content


def fetch_project_files(project_names: list[str], filename: str, batch_size: int = 100):
    """Fetch file in batches for all given projects via GitHub's GraphQL API."""
    headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
    try:
        project_files = {}
        for project_batch in batch_list(project_names, batch_size):
            payload = {"query": build_project_files_query(project_batch, filename)}
            url = BASE_URL + GRAPHQL_ENDPOINT
            response = httpx.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            for proj_name, files in response.json()["data"]["repository"].items():
                project_files[proj_name] = files[sanitize(filename)] if files else None
    except httpx.HTTPError:  # Rough fallback, to allow demo to proceed if API fails
        project_files = {}
        projects = load_projects_from_local_file("fallback.json")
        for project_name in project_names:
            proj = projects[project_name]
            project_files[sanitize(proj.name)] = getattr(proj, sanitize(filename), None)
    return project_files


def build_project_files_query(project_names: list[str], filename: str) -> str:
    """Build query for fetching file for all given projects via GitHub's GraphQL API."""
    inner_fragments = []
    for pname in project_names:
        sanitized_pname = sanitize(pname)
        inner_fragments.append(
            f"""
            {sanitized_pname}: object(expression: "HEAD:projects/{pname}/{filename}") {{
                ... on Blob {{
                    {sanitize(filename)}: text
                }}
            }}
            """
        )
    inner = "\n".join(inner_fragments)
    query = f"""
        {{
            repository(owner: "google", name: "oss-fuzz") {{
                {inner}
            }}
        }}
    """
    return query
