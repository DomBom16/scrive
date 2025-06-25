from typing import Union

from .core import Scrive


def word_boundary() -> Scrive:
    """Create word boundary assertion."""
    return Scrive("\\b")


def non_word_boundary() -> Scrive:
    """Create non-word boundary assertion."""
    return Scrive("\\B")


def after(pattern: Union[Scrive, str]) -> Scrive:
    """Create positive lookbehind assertion."""
    lookbehind = pattern.pattern if isinstance(pattern, Scrive) else str(pattern)
    return Scrive(f"(?<={lookbehind})")


def before(pattern: Union[Scrive, str]) -> Scrive:
    """Create positive lookahead assertion."""
    lookahead = pattern.pattern if isinstance(pattern, Scrive) else str(pattern)
    return Scrive(f"(?={lookahead})")


def not_after(pattern: Union[Scrive, str]) -> Scrive:
    """Create negative lookbehind assertion."""
    lookbehind = pattern.pattern if isinstance(pattern, Scrive) else str(pattern)
    return Scrive(f"(?<!{lookbehind})")


def not_before(pattern: Union[Scrive, str]) -> Scrive:
    """Create negative lookahead assertion."""
    lookahead = pattern.pattern if isinstance(pattern, Scrive) else str(pattern)
    return Scrive(f"(?!{lookahead})")
