"""Load Data"""

import json

import yaml

from models import Project, ProjectFile


def load_project_from_files(
    project_name: str, project_yaml: str | None, build_sh: str | None
) -> Project:
    """Load a project from its project_yaml and build_sh files."""
    project_yaml_dict = yaml.safe_load(project_yaml or "")
    project = Project(
        name=project_name,
        language=project_yaml_dict.get("language"),
        homepage=project_yaml_dict.get("homepage"),
        main_repo=project_yaml_dict.get("main_repo"),
        primary_contact=project_yaml_dict.get("primary_contact"),
        vendor_ccs=project_yaml_dict.get("vendor_ccs"),
        fuzzing_engines=project_yaml_dict.get("fuzzing_engines"),
        build_system=infer_build_system(build_sh) if build_sh is not None else None,
        project_yaml=ProjectFile(project_yaml) if project_yaml is not None else None,
        build_sh=ProjectFile(build_sh) if build_sh is not None else None,
    )
    return project


def load_projects_from_local_file(filepath: str):
    """Load projects from a local json file."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw_projects = json.load(f)
    projects = {pname: Project(**raw_proj) for pname, raw_proj in raw_projects.items()}
    return projects


def infer_build_system(file_content: str) -> str:
    """Heuristically infer the build system used in a file."""
    file = file_content.lower()
    if "cmake" in file:
        return "cmake"
    if "make" in file:
        return "make"
    if "ninja" in file:
        return "ninja"
    if "bazel" in file:
        return "bazel"
    return "unknown"
