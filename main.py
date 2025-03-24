"""OSS-Fuzz-Research"""

import base64

import httpx
import yaml
from dotenv import load_dotenv

load_dotenv()


PROJECTS_ENDPOINT = "https://api.github.com/repos/google/oss-fuzz/contents/projects"
PROJECT_YAML_ENDPOINT = "https://api.github.com/repos/google/oss-fuzz/contents/projects/{project_name}/project.yaml"
BUILD_SH_ENDPOINT = "https://api.github.com/repos/google/oss-fuzz/contents/projects/{project_name}/build.sh"


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


def infer_build_system(file: str):
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


def get_project_details(project_name: str):
    url = PROJECT_YAML_ENDPOINT.format(project_name=project_name)
    response = httpx.get(url)
    project = yaml.safe_load(base64.b64decode(response.json()["content"]))

    url = BUILD_SH_ENDPOINT.format(project_name=project_name)
    response = httpx.get(url)
    build_file = base64.b64decode(response.json()["content"]).decode()
    build_system = infer_build_system(build_file)

    metadata = {
        "name": project_name,
        "language": project.get("language"),
        "homepage": project.get("homepage"),
        "main_repo": project.get("main_repo"),
        "primary_contact": project.get("primary_contact"),
        "vendor_ccs": project.get("vendor_ccs", []),
        "fuzzing_engines": project.get("fuzzing_engines", []),
        "build_system": build_system,
    }
    return metadata
