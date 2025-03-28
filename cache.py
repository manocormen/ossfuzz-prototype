"""Cache Data"""

from models import Projects


class Cache:
    """Data cache."""

    def __init__(self) -> None:
        self.projects: Projects = {}

    def __len__(self) -> int:
        return len(self.projects)

    def __bool__(self) -> bool:
        return len(self) > 0
