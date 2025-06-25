import re
from typing import Union

from .standalone import exactly
from .core import Scrive


def one_or_more(*patterns: Union[Scrive, str]) -> Scrive:
    """Apply `+` quantifier to patterns."""
    if len(patterns) == 1:
        pattern = patterns[0]
        if isinstance(pattern, Scrive):
            return pattern.one_or_more()
        else:
            return Scrive(re.escape(str(pattern))).one_or_more()
    else:
        # Combine multiple patterns and apply quantifier
        combined = Scrive()
        for pattern in patterns:
            if isinstance(pattern, Scrive):
                combined = combined + pattern
            else:
                combined = combined + exactly(str(pattern))
        return combined.one_or_more()


def zero_or_more(*patterns: Union[Scrive, str]) -> Scrive:
    """Apply `*` quantifier to patterns."""
    if len(patterns) == 1:
        pattern = patterns[0]
        if isinstance(pattern, Scrive):
            return pattern.zero_or_more()
        else:
            return Scrive(re.escape(str(pattern))).zero_or_more()
    else:
        # Combine multiple patterns and apply quantifier
        combined = Scrive()
        for pattern in patterns:
            if isinstance(pattern, Scrive):
                combined = combined + pattern
            else:
                combined = combined + exactly(str(pattern))
        return combined.zero_or_more()


def maybe(*patterns: Union[Scrive, str]) -> Scrive:
    """Apply `?` quantifier to patterns."""
    if len(patterns) == 1:
        pattern = patterns[0]
        if isinstance(pattern, Scrive):
            return pattern.maybe()
        else:
            return Scrive(re.escape(str(pattern))).maybe()
    else:
        # Combine multiple patterns and apply quantifier
        combined = Scrive()
        for pattern in patterns:
            if isinstance(pattern, Scrive):
                combined = combined + pattern
            else:
                combined = combined + exactly(str(pattern))
        return combined.maybe()
