"""
Scrive - Fluent Regex Pattern Builder

A modern, unified regex pattern builder for Python that makes complex regular
expressions readable, maintainable, and discoverable.

Quick Start:
    >>> from scrive import S
    >>> pattern = S.digit().one_or_more().anchor_string()
    >>> pattern.test("123")  # True

Main Classes:
    S: Unified factory class - preferred entry point
    Scrive: Core pattern class with chainable methods

For more examples and documentation, visit: https://github.com/your-repo/scrive
"""

# Main unified API exports
# Common patterns for convenience
# Useful macros
from .scrive import (
    S,
    Scrive,
    choice,
    create,
    credit_card,
    decimal_range,
    email,
    ipv4,
    ipv6,
    phone_number,
    separated_by,
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

# Version info
__version__ = "0.2.0"
__author__ = "Domenic Urso"
__email__ = "domenicjurso@gmail.com"
__description__ = "A fluent regex pattern builder for Python"
