"""Define Utility Functions"""

from typing import Iterator


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


def sanitize(identifier: str) -> str:
    """Replace invalid characters in identifier with underscores."""
    return identifier.replace(".", "_").replace("-", "_")


def batch_list(list_: list, batch_size: int) -> Iterator[list]:
    """Break input list into batches."""
    for i in range(0, len(list_), batch_size):
        yield list_[i : i + batch_size]
