"""Interact with API"""

from collections.abc import Callable

from dotenv import load_dotenv

from cache import Cache
from fetcher import fetch_project_file, fetch_project_files, fetch_project_names
from loader import load_project_from_files
from models import Project, Projects
from utils import sanitize

load_dotenv()

BATCH_SIZE = 200

_cache = Cache()


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


def get_projects(limit: int | None = None) -> Projects:
    """Return the details of all projects."""
    if not _cache:
        cache_projects(limit)
    return _cache.projects


def filter_projects(predicate: Callable, limit: int | None = None) -> Projects:
    """Return the details of all projects that satisfy the predicate."""
    if not _cache:
        cache_projects(limit)
    return {name: proj for name, proj in _cache.projects.items() if predicate(proj)}


def match_projects(
    name: str | None = None,
    language: str | None = None,
    homepage: str | None = None,
    main_repo: str | None = None,
    primary_contact: str | None = None,
    vendor_ccs: list[str] | None = None,
    fuzzing_engines: list[str] | None = None,
    build_system: str | None = None,
    limit: int | None = None,
) -> Projects:
    """Return the details of all the projects that match all the given keywords."""
    keywords = {k: v for k, v in locals().items() if (v is not None and k != "limit")}

    def is_match(project: Project) -> bool:
        """Return true if the given project matches all the keywords in the closure."""
        for attr_name, keyword in keywords.items():
            attr_value = getattr(project, attr_name)
            if not attr_value or keyword not in attr_value:
                return False  # If a single keyword is missing, no match, return early
        return True

    return filter_projects(is_match, limit)


def cache_projects(limit: int | None = None) -> None:
    """Cache the projects, up to limit."""
    print("Please wait: Fetching project data... (~45s, only once)")
    project_names = list_projects(limit)
    build_sh_files = fetch_project_files(project_names, "build.sh", BATCH_SIZE)
    print("We're halfway there...")
    project_yaml_files = fetch_project_files(project_names, "project.yaml", BATCH_SIZE)
    print("Caching complete!")
    projects: Projects = {}
    for project_name in project_names:
        project_yaml = project_yaml_files[sanitize(project_name)]
        build_sh = build_sh_files[sanitize(project_name)]
        project = load_project_from_files(project_name, project_yaml, build_sh)
        projects[project_name] = project
    _cache.projects = projects


def clear_cache() -> None:
    """Remove all items from the cache."""
    _cache.clear()
