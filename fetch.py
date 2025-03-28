"""Fetch Data"""

import base64
import os
from typing import Iterator

import httpx

BASE_URL = "https://api.github.com"
CONTENTS_ENDPOINT = "/repos/google/oss-fuzz/contents"
GRAPHQL_ENDPOINT = "/graphql"


def fetch_project_names() -> list[str]:
    """Fetch the names of all projects via GitHub's REST API."""
    response = httpx.get(BASE_URL + CONTENTS_ENDPOINT + "/projects")
    projects = [project["name"] for project in response.json()]
    return projects


def fetch_project_file(project_name: str, filename: str) -> str:
    """Fetch file for specific project via GitHub's REST API."""
    url = BASE_URL + CONTENTS_ENDPOINT + f"/projects/{project_name}/{filename}"
    response = httpx.get(url)
    file_content = base64.b64decode(response.json().get("content", "")).decode()
    return file_content


def fetch_project_files(project_names: list[str], filename: str, batch_size: int = 100):
    """Fetch file in batches for all given projects via GitHub's GraphQL API."""
    headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
    project_files = {}
    for pname in batch_list(project_names, batch_size):
        payload = {"query": build_project_files_query(pname, filename)}
        url = BASE_URL + GRAPHQL_ENDPOINT
        response = httpx.post(url, headers=headers, json=payload, timeout=30)
        for project_name, files in response.json()["data"]["repository"].items():
            project_files[project_name] = (
                files[sanitize_identifier(filename)] if files else None
            )
    return project_files


def build_project_files_query(project_names: list[str], filename: str) -> str:
    """Build query for fetching file for all given projects via GitHub's GraphQL API."""
    inner_fragments = []
    for pname in project_names:
        sanitized_pname = sanitize_identifier(pname)
        inner_fragments.append(
            f"""
            {sanitized_pname}: object(expression: "HEAD:projects/{pname}/{filename}") {{
                ... on Blob {{
                    {sanitize_identifier(filename)}: text
                }}
            }}
            """
        )
    query = f"""
        {{
            repository(owner: "google", name: "oss-fuzz") {{
                {'\n'.join(inner_fragments)}
            }}
        }}
    """
    return query


def sanitize_identifier(identifier: str) -> str:
    """Replace invalid characters in identifier with underscores."""
    return identifier.replace(".", "_").replace("-", "_")


def batch_list(list_: list, batch_size: int) -> Iterator[list]:
    """Break input list into batches."""
    for i in range(0, len(list_), batch_size):
        yield list_[i : i + batch_size]
