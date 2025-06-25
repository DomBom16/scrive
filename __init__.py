"""
Scrive - A Pythonic regex pattern builder library.

Scrive provides a chainable, fluent interface for building complex regular expressions
with readable, maintainable code. It supports method chaining, named capture groups,
and common regex patterns out of the box.

Example usage:
    from scrive import exactly, digit, one_or_more, create

    # Simple pattern
    pattern = exactly("hello").ignore_case()

    # Complex pattern with groups
    email_pattern = (
        one_or_more(word_char())
        .grouped_as("username")
        .and_("@")
        .and_(one_or_more(word_char()).grouped_as("domain"))
    )

    # Using operators
    greeting = exactly("hello") + exactly(" ") + exactly("world")
    choice = exactly("cat") | exactly("dog")
"""

from .scrive.anchors import end_of_line, end_of_string, start_of_line, start_of_string
from .scrive.assertions import (
    after,
    before,
    non_word_boundary,
    not_after,
    not_before,
    word_boundary,
)
from .scrive.standalone import (
    alphanumeric,
    any_char,
    ascii,
    carriage_return,
    char,
    char_range,
    digit,
    exactly,
    hexadecimal,
    letter,
    lowercase,
    newline,
    non_ascii,
    non_digit,
    non_whitespace,
    non_word_char,
    none_of,
    one_of,
    tab,
    uppercase,
    whitespace,
    word_char,
)
from .scrive.core import Scrive
from .scrive.flags import (
    DOTALL,
    IGNORECASE,
    MULTILINE,
    VERBOSE,
    dotall,
    ignore_case,
    lazy,
    multiline,
    verbose,
)
from .scrive.grouping import group, grouped_as, non_capturing_group, reference_to
from .scrive.macros import choice, create, decimal_range, separated_by
from .scrive.patterns import (
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
from .scrive.quantifiers import maybe, one_or_more, zero_or_more

__version__ = "1.0.0"
__author__ = "Scrive Contributors"
__description__ = "A Pythonic regex pattern builder library"

__all__ = [
    # Core
    "Scrive",
    # Anchors
    "start_of_line",
    "end_of_line",
    "start_of_string",
    "end_of_string",
    "word_boundary",
    "non_word_boundary",
    # Assertions
    "after",
    "before",
    "not_after",
    "not_before",
    # Characters
    "char",
    "any_char",
    "word_char",
    "letter",
    "digit",
    "whitespace",
    "non_whitespace",
    "ascii",
    "non_ascii",
    "non_digit",
    "non_word_char",
    "tab",
    "newline",
    "carriage_return",
    "lowercase",
    "uppercase",
    "alphanumeric",
    "hexadecimal",
    "exactly",
    "one_of",
    "none_of",
    "char_range",
    # Grouping
    "group",
    "grouped_as",
    "non_capturing_group",
    "reference_to",
    # Macros
    "separated_by",
    "decimal_range",
    "choice",
    "create",
    # Patterns
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
    # Quantifiers
    "zero_or_more",
    "one_or_more",
    "maybe",
    # Flags
    "MULTILINE",
    "DOTALL",
    "VERBOSE",
    "IGNORECASE",
    "multiline",
    "dotall",
    "verbose",
    "ignore_case",
    "lazy",
    # Unicode support
    "unicode_category",
    "unicode_script",
    "unicode_block",
    "not_unicode_category",
    "not_unicode_script",
    "not_unicode_block",
    "unicode_letter",
    "unicode_uppercase",
    "unicode_lowercase",
    "unicode_digit",
    "unicode_number",
    "unicode_punctuation",
    "unicode_symbol",
    "unicode_whitespace",
    "unicode_mark",
    "unicode_control",
    "unicode_latin",
    "unicode_cyrillic",
    "unicode_greek",
    "unicode_arabic",
    "unicode_hebrew",
    "unicode_han",
    "unicode_hiragana",
    "unicode_katakana",
    "unicode_hangul",
    "unicode_devanagari",
    "unicode_basic_latin",
    "unicode_emoji",
    "describe_unicode_category",
    "describe_unicode_script",
    "describe_unicode_block",
    "list_unicode_categories",
    "list_unicode_scripts",
    "list_unicode_blocks",
]
