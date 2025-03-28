"""Define Utility Functions"""

from typing import Iterator


def sanitize(identifier: str) -> str:
    """Replace invalid characters in identifier with underscores."""
    return identifier.replace(".", "_").replace("-", "_")


def batch_list(list_: list, batch_size: int) -> Iterator[list]:
    """Break input list into batches."""
    for i in range(0, len(list_), batch_size):
        yield list_[i : i + batch_size]
