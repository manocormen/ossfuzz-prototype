"""Define Data Models"""

import json
from dataclasses import asdict, dataclass, field


@dataclass
class ProjectFile:
    """Project File Model."""

    content: str = ""

    def __repr__(self):
        return f"'{self.content[:10]}...'"


@dataclass
class Project:
    """Project Model."""

    name: str = ""
    language: str = ""
    homepage: str = ""
    main_repo: str = ""
    primary_contact: str = ""
    vendor_ccs: list[str] = field(default_factory=list)
    fuzzing_engines: list[str] = field(default_factory=list)
    build_system: str | None = None
    project_yaml: ProjectFile | None = None
    build_sh: ProjectFile | None = None

    def to_dict(self) -> dict:
        """Return project as a dict."""
        return asdict(self)

    def to_json(self) -> str:
        """Return project as json."""
        return json.dumps(asdict(self), indent=4)


type Projects = dict[str, Project]
