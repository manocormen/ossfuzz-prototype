"""Interact with API"""

from dotenv import load_dotenv

from fetcher import fetch_project_file, fetch_project_files, fetch_project_names
from loader import load_project_from_files
from models import Project, Projects
from utils import sanitize

load_dotenv()

BATCH_SIZE = 200

_projects_cache = {}


def list_projects(limit: int | None = None) -> list[str]:
    """Return the names of projects, up to limit."""
    projects = fetch_project_names()
    return projects if limit is None else projects[:limit]


def get_project(project_name: str) -> Project:
    """Return the details of a specific project."""
    project_yaml = fetch_project_file(project_name, "project.yaml")
    build_sh = fetch_project_file(project_name, "build.sh")
    project = load_project_from_files(project_name, project_yaml, build_sh)
    return project


def cache_projects(limit: int | None = None) -> None:
    """Cache the projects, up to limit."""
    print("Please wait: caching project data... (just once)")
    project_names = list_projects(limit)
    project_yaml_files = fetch_project_files(project_names, "project.yaml", BATCH_SIZE)
    build_sh_files = fetch_project_files(project_names, "build.sh", BATCH_SIZE)
    projects: Projects = {}
    for project_name in project_names:
        project_yaml = project_yaml_files[sanitize(project_name)]
        build_sh = build_sh_files[sanitize(project_name)]
        project = load_project_from_files(project_name, project_yaml, build_sh)
        projects[project_name] = project
    global _projects_cache
    _projects_cache = projects
