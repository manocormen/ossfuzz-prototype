"""OSS-Fuzz-Research"""

import base64

import httpx
import yaml
from dotenv import load_dotenv

load_dotenv()


PROJECTS_ENDPOINT = "https://api.github.com/repos/google/oss-fuzz/contents/projects"
PROJECT_YAML_ENDPOINT = "https://api.github.com/repos/google/oss-fuzz/contents/projects/{project_name}/project.yaml"


def get_all_projects():
    response = httpx.get(PROJECTS_ENDPOINT)
    projects = [
        {
            "name": project["name"],
            "url": project["html_url"],
        }
        for project in response.json()
    ]
    return projects


def get_project_details(project_name: str):
    url = PROJECT_YAML_ENDPOINT.format(project_name=project_name)
    response = httpx.get(url)
    project = yaml.safe_load(base64.b64decode(response.json()["content"]))
    metadata = {
        "name": project_name,
        "language": project.get("language"),
        "homepage": project.get("homepage"),
        "main_repo": project.get("main_repo"),
        "primary_contact": project.get("primary_contact"),
        "vendor_ccs": project.get("vendor_ccs", []),
        "fuzzing_engines": project.get("fuzzing_engines", []),
    }
    return metadata
