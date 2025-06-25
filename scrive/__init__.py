"""
Scrive - A fluent regex pattern builder for Python.

Unified API for building complex regex patterns with chainable methods.

Quick Start:
    >>> from scrive import S
    >>> pattern = S.digit().one_or_more().anchor_string()
    >>> pattern.test("123")  # True

Main Classes:
    S: Unified factory class - preferred entry point
    Scrive: Core pattern class with chainable methods

For more examples and documentation, visit: https://github.com/your-repo/scrive
"""

from .core import Scrive
from .factory import S

# Useful macros
from .macros import choice, create, decimal_range, separated_by

# Common patterns for convenience
from .patterns import (
    credit_card,
    email,
    ipv4,
    ipv6,
    phone_number,
    url,
    uuidv1,
    uuidv2,
    uuidv3,
    uuidv4,
    uuidv5,
    uuidv6,
    uuidv7,
    uuidv8,
)

# Main exports - unified API
__all__ = [
    # Primary unified API
    "S",
    "Scrive",
    # Common patterns
    "email",
    "url",
    "ipv4",
    "ipv6",
    "phone_number",
    "credit_card",
    "uuidv1",
    "uuidv2",
    "uuidv3",
    "uuidv4",
    "uuidv5",
    "uuidv6",
    "uuidv7",
    "uuidv8",
    # Useful macros
    "choice",
    "create",
    "decimal_range",
    "separated_by",
]


# Method delegation - allows both S.digit() and Scrive.digit()
# This is done here to avoid circular imports between factory and core
def _add_factory_methods_to_scrive():
    """Add S factory methods as static methods to Scrive class"""
    import inspect

    for name, method in inspect.getmembers(S, predicate=inspect.isfunction):
        if not name.startswith("_") and not hasattr(Scrive, name):
            setattr(Scrive, name, staticmethod(method))


# Apply the delegation after all imports are complete
_add_factory_methods_to_scrive()

# Version info
__version__ = "0.2.0"
__author__ = "Domenic Urso"
__email__ = "domenicjurso@gmail.com"
__description__ = "A fluent regex pattern builder for Python"
