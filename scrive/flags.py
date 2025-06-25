import re
from typing import Union

from .core import Scrive


def ignore_case(pattern: Union[Scrive, str]) -> Scrive:
    """Add case-insensitive flag to pattern."""
    if isinstance(pattern, Scrive):
        return Scrive(pattern.pattern, pattern.flags | re.IGNORECASE)
    else:
        return Scrive(str(pattern), re.IGNORECASE)


def multiline(pattern: Union[Scrive, str]) -> Scrive:
    """Add multiline flag to pattern."""
    if isinstance(pattern, Scrive):
        return Scrive(pattern.pattern, pattern.flags | re.MULTILINE)
    else:
        return Scrive(str(pattern), re.MULTILINE)


def dotall(pattern: Union[Scrive, str]) -> Scrive:
    """Add dotall flag to pattern (`.` matches newlines)."""
    if isinstance(pattern, Scrive):
        return Scrive(pattern.pattern, pattern.flags | re.DOTALL)
    else:
        return Scrive(str(pattern), re.DOTALL)


def verbose(pattern: Union[Scrive, str]) -> Scrive:
    """Add verbose flag for readable regex."""
    if isinstance(pattern, Scrive):
        return Scrive(pattern.pattern, pattern.flags | re.VERBOSE)
    else:
        return Scrive(str(pattern), re.VERBOSE)


def lazy(pattern: Union[Scrive, str]) -> Scrive:
    """Make quantifier lazy (non-greedy)."""
    if isinstance(pattern, Scrive):
        pattern_str = pattern.pattern
        flags = pattern.flags
    else:
        pattern_str = str(pattern)
        flags = 0

    if pattern_str.endswith(("+", "*", "?", "}")):
        return Scrive(f"{pattern_str}?", flags)
    return Scrive(pattern_str, flags)


# RE Flag constants as Scrive instances
IGNORECASE = Scrive("", re.IGNORECASE)
MULTILINE = Scrive("", re.MULTILINE)
DOTALL = Scrive("", re.DOTALL)
VERBOSE = Scrive("", re.VERBOSE)
