import re
from typing import Optional, Union

from .core import Scrive


def _optimize_char_class(chars: str) -> str:
    """Optimize character class construction."""
    if not chars:
        return ""

    # Sort and deduplicate
    unique_chars = "".join(sorted(set(chars)))

    # Check for ranges
    optimized = []
    i = 0
    while i < len(unique_chars):
        start = i
        # Find consecutive ASCII characters
        while (
            i + 1 < len(unique_chars)
            and ord(unique_chars[i + 1]) == ord(unique_chars[i]) + 1
        ):
            i += 1

        if i - start >= 2:  # Range of 3+ chars
            # Escape start and end characters but not the dash
            optimized.append(
                f"{re.escape(unique_chars[start])}-{re.escape(unique_chars[i])}"
            )
        else:
            # Escape individual characters
            for j in range(start, i + 1):
                optimized.append(re.escape(unique_chars[j]))
        i += 1

    return "".join(optimized)


_ANY_CHAR = Scrive(".")
_DIGIT = Scrive("\\d")
_NON_DIGIT = Scrive("\\D")
_WORD_CHAR = Scrive("\\w")
_ASCII = Scrive("[ -~]")
_NON_ASCII = Scrive("[^ -~]")
_NON_WORD_CHAR = Scrive("\\W")
_WHITESPACE = Scrive("\\s")
_NON_WHITESPACE = Scrive("\\S")
_TAB = Scrive("\\t")
_NEWLINE = Scrive("\\n")
_CARRIAGE_RETURN = Scrive("\\r")
_LOWERCASE = Scrive("[a-z]")
_UPPERCASE = Scrive("[A-Z]")
_LETTER = Scrive("[a-zA-Z]")
_ALPHANUMERIC = Scrive("[a-zA-Z0-9]")
_HEXADECIMAL = Scrive("[0-9a-fA-F]")


def char(chars: Optional[str] = None) -> Scrive:
    """Match any character, or specific characters if provided."""
    if chars is None:
        return _ANY_CHAR
    elif len(chars) == 1:
        return Scrive(re.escape(chars))
    else:
        optimized = _optimize_char_class(chars)
        return Scrive(f"[{optimized}]")


def any_char() -> Scrive:
    """Match any character - `.`"""
    return _ANY_CHAR


def digit() -> Scrive:
    """Match any digit - `\\d`"""
    return _DIGIT


def non_digit() -> Scrive:
    """Match any non-digit - `\\D`"""
    return _NON_DIGIT


def word_char() -> Scrive:
    """Match any word character - `\\w`"""
    return _WORD_CHAR


def non_word_char() -> Scrive:
    """Match any non-word character - `\\W`"""
    return _NON_WORD_CHAR


def ascii() -> Scrive:
    """Match any ASCII character - `[ -~]`"""
    return _ASCII


def non_ascii() -> Scrive:
    """Match any non-ASCII character - `[^ -~]`"""
    return _NON_ASCII


def whitespace() -> Scrive:
    """Match any whitespace character - `\\s`"""
    return _WHITESPACE


def non_whitespace() -> Scrive:
    """Match any non-whitespace character - `\\S`"""
    return _NON_WHITESPACE


def tab() -> Scrive:
    """Match tab character - `\\t`"""
    return _TAB


def newline() -> Scrive:
    """Match newline character - `\\n`"""
    return _NEWLINE


def carriage_return() -> Scrive:
    """Match carriage return - `\\r`"""
    return _CARRIAGE_RETURN


def letter() -> Scrive:
    """Match any letter - `[a-zA-Z]`"""
    return _LETTER


def lowercase() -> Scrive:
    """Match lowercase letter - `[a-z]`"""
    return _LOWERCASE


def uppercase() -> Scrive:
    """Match uppercase letter - `[A-Z]`"""
    return _UPPERCASE


def alphanumeric() -> Scrive:
    """Match alphanumeric character - `[a-zA-Z0-9]`"""
    return _ALPHANUMERIC


def hexadecimal() -> Scrive:
    """Match hexadecimal digit - `[0-9a-fA-F]`"""
    return _HEXADECIMAL


def exactly(text: str) -> Scrive:
    """Match exact text (escaped)."""
    return Scrive(re.escape(text))


def one_of(*items: str) -> Scrive:
    """Match any one of the provided characters or strings intelligently.

    If all items are single characters, creates a character class [abc].
    If any items are multi-character strings, uses alternation (word1|word2).
    """
    if not items:
        raise ValueError(
            "one_of() requires at least one item. Provide characters or strings to match."
        )

    # Check if all items are single characters
    all_single_chars = all(len(item) == 1 for item in items)

    if all_single_chars:
        # Character class behavior for single characters
        if len(items) == 1:
            return Scrive(re.escape(items[0]))

        all_chars = "".join(items)
        optimized = _optimize_char_class(all_chars)
        return Scrive(f"[{optimized}]")
    else:
        if len(items) == 1:
            return exactly(items[0])

        return Scrive(
            Scrive("")._optimize_alternation([re.escape(str(item)) for item in items])
        )


def none_of(*chars: str) -> Scrive:
    """Match any character except the provided ones."""
    all_chars = "".join(chars)
    optimized = _optimize_char_class(all_chars)
    return Scrive(f"[^{optimized}]")


def char_range(start: str, end: str) -> Scrive:
    """Match character range `[start-end]`."""
    return Scrive(f"[{re.escape(start)}-{re.escape(end)}]")


def raw(regex: str) -> Scrive:
    """Create pattern with raw regex injection without escaping."""
    return Scrive(regex)


def invert(pattern: Union[Scrive, str]) -> Scrive:
    """Invert/negate a pattern."""
    if isinstance(pattern, Scrive):
        return pattern.invert()
    else:
        # For string patterns, create Scrive object first
        scrive_pattern = exactly(pattern)
        return scrive_pattern.invert()


def ref(group_number: int) -> Scrive:
    """Create numbered backreference \\n."""
    return Scrive(f"\\{group_number}")


def case_insensitive(pattern: Union[Scrive, str]) -> Scrive:
    """Wrap pattern in case-insensitive group (?i:...)."""
    if isinstance(pattern, Scrive):
        inner = pattern.pattern
    else:
        inner = re.escape(str(pattern))
    return Scrive(f"(?i:{inner})")


def case_sensitive(pattern: Union[Scrive, str]) -> Scrive:
    """Wrap pattern in case-sensitive group (?-i:...)."""
    if isinstance(pattern, Scrive):
        inner = pattern.pattern
    else:
        inner = re.escape(str(pattern))
    return Scrive(f"(?-i:{inner})")


def template(
    template_pattern: Union[Scrive, str], **kwargs: Union[str, Scrive]
) -> Scrive:
    """Create pattern from template with variable substitution."""
    if isinstance(template_pattern, Scrive):
        return template_pattern.template(**kwargs)
    else:
        scrive_template = Scrive(template_pattern)
        return scrive_template.template(**kwargs)


def anchor_start() -> Scrive:
    """Create start of string anchor ^."""
    return Scrive("^")


def anchor_end() -> Scrive:
    """Create end of string anchor $."""
    return Scrive("$")


def anchor_both() -> Scrive:
    """Create start and end of string anchors ^...$."""
    return Scrive("^$")
