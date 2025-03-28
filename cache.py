"""Cache Data"""

from models import Projects


class Cache:
    """Data cache."""

    def __init__(self) -> None:
        self.projects: Projects = {}
