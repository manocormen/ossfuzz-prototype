"""Internal module for fetching OSS-Fuzz project data"""

import base64
import os

import httpx

type Project = dict[str, str | list[str]]
type Projects = dict[str, Project]

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


def fetch_project_files(project_names: list[str], filename: str) -> Projects:
    """Fetch file for all given projects via GitHub's GraphQL API."""
    headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
    payload = {"query": build_project_files_query(project_names, filename)}
    response = httpx.post(
        BASE_URL + GRAPHQL_ENDPOINT, headers=headers, json=payload, timeout=30
    )
    projects = response.json()["data"]["repository"]
    return projects


def build_project_files_query(project_names: list[str], filename: str) -> str:
    """Build query for fetching file for all given projects via GitHub's GraphQL API."""
    inner_fragment = "\n".join(
        [
            f"""
                {pname}: object(expression: "HEAD:projects/{pname}/{filename}") {{
                    ... on Blob {{
                        {sanitize_identifier(filename)}: text
                    }}
                }}
            """
            for pname in [sanitize_identifier(pname) for pname in project_names]
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


def sanitize_identifier(identifier: str) -> str:
    """Replace invalid characters in identifier with underscores."""
    return identifier.replace(".", "_").replace("-", "_")
