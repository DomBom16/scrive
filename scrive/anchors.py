import re

from .core import Scrive


def start_of_string() -> Scrive:
    """Create start of string anchor ^."""
    return Scrive("^")


def end_of_string() -> Scrive:
    """Create end of string anchor $."""
    return Scrive("$")


def start_of_line() -> Scrive:
    """Create start of line anchor (with MULTILINE flag)."""
    return Scrive("^", re.MULTILINE)


def end_of_line() -> Scrive:
    """Create end of line anchor (with MULTILINE flag)."""
    return Scrive("$", re.MULTILINE)
