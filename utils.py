"""Define Utility Functions"""


def sanitize(identifier: str) -> str:
    """Replace invalid characters in identifier with underscores."""
    return identifier.replace(".", "_").replace("-", "_")
