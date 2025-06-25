from typing import Optional, Union

from .core import Scrive


def reference_to(group_name: str) -> Scrive:
    """Create a backreference to a named group."""
    return Scrive(f"(?P={group_name})")


def group(pattern: Union[Scrive, str], name: Optional[str] = None) -> Scrive:
    """Create a capture group (named if name provided)."""
    if isinstance(pattern, Scrive):
        inner = pattern.pattern
    else:
        inner = str(pattern)

    if name:
        return Scrive(f"(?P<{name}>{inner})")
    else:
        return Scrive(f"({inner})")


def grouped_as(pattern: Union[Scrive, str], name: str) -> Scrive:
    """Create a named capture group."""
    if isinstance(pattern, Scrive):
        inner = pattern.pattern
    else:
        inner = str(pattern)
    return Scrive(f"(?P<{name}>{inner})")


def non_capturing_group(pattern: Union[Scrive, str]) -> Scrive:
    """Create a non-capturing group."""
    if isinstance(pattern, Scrive):
        inner = pattern.pattern
    else:
        inner = str(pattern)
    return Scrive(f"(?:{inner})")
