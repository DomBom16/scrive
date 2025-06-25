"""
Unified factory class for creating Scrive patterns.

This module provides the S factory class which serves as the main entry point
for creating regex patterns with Scrive. All pattern creation should go through
this factory for consistency and discoverability.
"""

import re
from typing import Optional, Union

from .core import Scrive


class S:
    """
    Unified factory for creating Scrive regex patterns.

    This class provides static methods organized by category to make
    pattern creation discoverable and consistent. All methods return
    Scrive instances that can be chained together.

    Example:
        >>> S.digit().one_or_more().anchor_string()
        >>> S.choice("cat", "dog", "bird").maybe()
        >>> S.literal("hello").whitespace().word().one_or_more()
    """

    # ================================
    # Pattern Creation - Literals & Text
    # ================================

    @staticmethod
    def literal(text: str) -> Scrive:
        """
        Create pattern matching exact text (escaped).

        Args:
            text: The literal text to match

        Returns:
            Scrive pattern matching the exact text

        Example:
            >>> S.literal("hello world")  # Matches "hello world" exactly
        """
        return Scrive(re.escape(text))

    @staticmethod
    def raw(regex: str) -> Scrive:
        """
        Create pattern from raw regex (unescaped).

        Args:
            regex: Raw regex pattern string

        Returns:
            Scrive pattern with the raw regex

        Example:
            >>> S.raw(r"\\d{3}-\\d{3}-\\d{4}")  # Phone number pattern
        """
        return Scrive(regex)
        
    @staticmethod
    def placeholder(name: str) -> Scrive:
        """
        Create pattern for a placeholder.

        Args:
            name: Name of the placeholder

        Returns:
            Scrive pattern matching the placeholder

        Example:
            >>> S.placeholder("name")  # Matches placeholder "name"
        """
        return Scrive(f"{{{name}}}")

    @staticmethod
    def char(*chars: str) -> Scrive:
        """
        Match any of the specified characters.

        Args:
            *chars: Characters to match

        Returns:
            Scrive pattern matching any of the characters

        Example:
            >>> S.char("a", "e", "i", "o", "u")  # Vowels [aeiou]
            >>> S.char("abc")  # Same as above but from string
        """
        if len(chars) == 1 and len(chars[0]) > 1:
            # Single string argument - treat each character separately
            all_chars = chars[0]
        else:
            # Multiple arguments
            all_chars = "".join(chars)

        if len(all_chars) == 1:
            return Scrive(re.escape(all_chars))

        # Sort and deduplicate
        unique_chars = "".join(sorted(set(all_chars)))

        # Build character class with ranges where possible
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
                optimized.append(
                    f"{re.escape(unique_chars[start])}-{re.escape(unique_chars[i])}"
                )
            else:
                # Individual characters
                for j in range(start, i + 1):
                    optimized.append(re.escape(unique_chars[j]))
            i += 1

        return Scrive(f"[{''.join(optimized)}]")

    @staticmethod
    def char_range(start: str, end: str) -> Scrive:
        """
        Create character range pattern.

        Args:
            start: Start character
            end: End character

        Returns:
            Scrive pattern matching characters in range

        Example:
            >>> S.char_range("a", "z")  # [a-z]
            >>> S.char_range("0", "9")  # [0-9]
        """
        return Scrive(f"[{re.escape(start)}-{re.escape(end)}]")

    @staticmethod
    def not_char(*chars: str) -> Scrive:
        """
        Match any character except the specified ones.

        Args:
            *chars: Characters to exclude

        Returns:
            Scrive pattern matching any character except those specified

        Example:
            >>> S.none_of("aeiou")  # Consonants [^aeiou]
        """
        if len(chars) == 1 and len(chars[0]) > 1:
            all_chars = chars[0]
        else:
            all_chars = "".join(chars)

        # Use same optimization as char() but with negation
        unique_chars = "".join(sorted(set(all_chars)))
        optimized = []
        i = 0
        while i < len(unique_chars):
            start = i
            while (
                i + 1 < len(unique_chars)
                and ord(unique_chars[i + 1]) == ord(unique_chars[i]) + 1
            ):
                i += 1

            if i - start >= 2:
                optimized.append(
                    f"{re.escape(unique_chars[start])}-{re.escape(unique_chars[i])}"
                )
            else:
                for j in range(start, i + 1):
                    optimized.append(re.escape(unique_chars[j]))
            i += 1

        return Scrive(f"[^{''.join(optimized)}]")

    # ================================
    # Common Character Classes
    # ================================

    @staticmethod
    def any_char() -> Scrive:
        """Match any character (.)"""
        return Scrive(".")

    @staticmethod
    def digit() -> Scrive:
        """Match any digit (\\d)"""
        return Scrive("\\d")

    @staticmethod
    def letter() -> Scrive:
        """Match any letter ([a-zA-Z])"""
        return Scrive("[a-zA-Z]")

    @staticmethod
    def word() -> Scrive:
        """Match any word character (\\w)"""
        return Scrive("\\w")

    @staticmethod
    def whitespace() -> Scrive:
        """Match any whitespace character (\\s)"""
        return Scrive("\\s")

    @staticmethod
    def lowercase() -> Scrive:
        """Match lowercase letter ([a-z])"""
        return Scrive("[a-z]")

    @staticmethod
    def uppercase() -> Scrive:
        """Match uppercase letter ([A-Z])"""
        return Scrive("[A-Z]")

    @staticmethod
    def alphanumeric() -> Scrive:
        """Match alphanumeric character ([a-zA-Z0-9])"""
        return Scrive("[a-zA-Z0-9]")
        
    @staticmethod
    def binary() -> Scrive:
        """Match binary digit ([01])"""
        return Scrive("[01]")
        
    @staticmethod
    def octal() -> Scrive:
        """Match octal digit ([0-7])"""
        return Scrive("[0-7]")
        
    @staticmethod
    def hex() -> Scrive:
        """Match hexadecimal digit ([0-9a-fA-F])"""
        return Scrive("[0-9a-fA-F]")
        
    @staticmethod
    def hexadecimal() -> Scrive:
        """Match hexadecimal digit ([0-9a-fA-F])"""
        return S.hex()
        
    @staticmethod
    def base64() -> Scrive:
        """Match base64 digit ([A-Za-z0-9+/])"""
        return Scrive("[A-Za-z0-9+\/]")
        
    @staticmethod
    def ascii() -> Scrive:
        """Match ASCII character ([ -~])"""
        return Scrive("[ -~]")

    # ================================
    # Negated Character Classes
    # ================================

    @staticmethod
    def not_digit() -> Scrive:
        """Match any non-digit (\\D)"""
        return S.digit().invert()
        
    @staticmethod
    def not_letter() -> Scrive:
        """Match any non-letter ([^a-zA-Z])"""
        return S.letter().invert()

    @staticmethod
    def not_word() -> Scrive:
        """Match any non-word character (\\W)"""
        return S.word().invert()

    @staticmethod
    def not_whitespace() -> Scrive:
        """Match any non-whitespace character (\\S)"""
        return S.whitespace().invert()

    @staticmethod
    def not_ascii() -> Scrive:
        """Match non-ASCII character ([^ -~])"""
        return S.ascii().invert()

    # ================================
    # Special Characters
    # ================================

    @staticmethod
    def tab() -> Scrive:
        """Match tab character (\\t)"""
        return Scrive("\\t")

    @staticmethod
    def newline() -> Scrive:
        """Match newline character (\\n)"""
        return Scrive("\\n")

    @staticmethod
    def carriage_return() -> Scrive:
        """Match carriage return (\\r)"""
        return Scrive("\\r")

    @staticmethod
    def space() -> Scrive:
        """Match literal space character"""
        return Scrive(" ")

    # ================================
    # Boundary Assertions
    # ================================

    @staticmethod
    def word_boundary() -> Scrive:
        """Match word boundary (\\b)"""
        return Scrive("\\b")

    @staticmethod
    def non_word_boundary() -> Scrive:
        """Match non-word boundary (\\B)"""
        return Scrive("\\B")

    # ================================
    # Anchors
    # ================================

    @staticmethod
    def start_of_string() -> Scrive:
        """Match start of string (^)"""
        return Scrive("^")

    @staticmethod
    def end_of_string() -> Scrive:
        """Match end of string ($)"""
        return Scrive("$")

    @staticmethod
    def start_of_line() -> Scrive:
        """Match start of line (^ with MULTILINE)"""
        return Scrive("^", re.MULTILINE)

    @staticmethod
    def end_of_line() -> Scrive:
        """Match end of line ($ with MULTILINE)"""
        return Scrive("$", re.MULTILINE)

    # ================================
    # Grouping & References
    # ================================

    @staticmethod
    def group(pattern: Union[Scrive, str], name: Optional[str] = None) -> Scrive:
        """
        Create a capture group.

        Args:
            pattern: Pattern to group
            name: Optional name for the group

        Returns:
            Scrive pattern with the group

        Example:
            >>> S.group(S.digit().one_or_more(), "number")  # (?P<number>\\d+)
        """
        if isinstance(pattern, Scrive):
            inner = pattern.pattern
        else:
            inner = re.escape(str(pattern))

        if name:
            return Scrive(f"(?P<{name}>{inner})")
        else:
            return Scrive(f"({inner})")

    @staticmethod
    def non_capturing_group(pattern: Union[Scrive, str]) -> Scrive:
        """
        Create a non-capturing group.

        Args:
            pattern: Pattern to group

        Returns:
            Scrive pattern with non-capturing group

        Example:
            >>> S.non_capturing_group(S.literal("hello").or_(S.literal("hi")))
        """
        if isinstance(pattern, Scrive):
            inner = pattern.pattern
        else:
            inner = re.escape(str(pattern))

        return Scrive(f"(?:{inner})")

    @staticmethod
    def reference(target: Union[str, int]) -> Scrive:
        """
        Create a backreference.

        Args:
            target: Group name (string) or number (int) to reference

        Returns:
            Scrive pattern with backreference

        Example:
            >>> S.reference("word")  # (?P=word)
            >>> S.reference(1)       # \\1
        """
        if isinstance(target, str):
            return Scrive(f"(?P={target})")
        else:
            return Scrive(f"\\{target}")

    # ================================
    # Combinators
    # ================================

    @staticmethod
    def choice(*patterns: Union[Scrive, str]) -> Scrive:
        """
        Create alternation (OR) pattern.

        Args:
            *patterns: Patterns to choose from

        Returns:
            Scrive pattern with alternation

        Example:
            >>> S.choice("cat", "dog", "bird")  # (cat|dog|bird)
        """
        if not patterns:
            raise ValueError("choice() requires at least one pattern")

        if len(patterns) == 1:
            pattern = patterns[0]
            return pattern if isinstance(pattern, Scrive) else S.literal(str(pattern))

        # Collect pattern strings
        pattern_strs = []
        flags = 0

        for pattern in patterns:
            if isinstance(pattern, Scrive):
                pattern_strs.append(pattern.pattern)
                flags |= pattern.flags
            else:
                pattern_strs.append(re.escape(str(pattern)))

        # Use optimization from core
        dummy_scrive = Scrive("", flags)
        combined = dummy_scrive._optimize_alternation(pattern_strs)
        return Scrive(combined, flags)

    @staticmethod
    def sequence(*patterns: Union[Scrive, str]) -> Scrive:
        """
        Create sequence (concatenation) pattern.

        Args:
            *patterns: Patterns to concatenate

        Returns:
            Scrive pattern with all patterns in sequence

        Example:
            >>> S.sequence(S.literal("hello"), S.space(), S.word().one_or_more())
        """
        result = Scrive()
        for pattern in patterns:
            if isinstance(pattern, Scrive):
                result = result + pattern
            else:
                result = result + S.literal(str(pattern))
        return result

    # ================================
    # Common Patterns
    # ================================

    @staticmethod
    def email() -> Scrive:
        """Match email address pattern"""
        from .patterns import email

        return email()

    @staticmethod
    def url() -> Scrive:
        """Match URL pattern"""
        from .patterns import url

        return url()

    @staticmethod
    def ipv4() -> Scrive:
        """Match IPv4 address pattern"""
        from .patterns import ipv4

        return ipv4()

    @staticmethod
    def ipv6() -> Scrive:
        """Match IPv6 address pattern"""
        from .patterns import ipv6

        return ipv6()

    @staticmethod
    def phone() -> Scrive:
        """Match phone number pattern"""
        from .patterns import phone_number

        return phone_number()

    @staticmethod
    def credit_card() -> Scrive:
        """Match credit card number pattern"""
        from .patterns import credit_card

        return credit_card()

    @staticmethod
    def uuid(version: Optional[int] = None) -> Scrive:
        """
        Match UUID pattern.

        Args:
            version: Specific UUID version (1-8), or None for any version

        Returns:
            Scrive pattern matching UUID

        Example:
            >>> S.uuid()     # Any UUID version
            >>> S.uuid(4)    # UUID v4 only
        """

        def _uuid(version: int) -> Scrive:
            S.any_char().group() + S.any_char().reference(1)

            return (
                S.hex().times(8)
                + S.literal("-")
                + S.hex().times(4)
                + S.literal("-")
                + S.literal(str(version))
                + S.hex().times(3)
                + S.literal("-")
                + S.char("89abAB")
                + S.hex().times(3)
                + S.literal("-")
                + S.hex().times(12)
            )

        if version is None:
            return S.choice(*[_uuid(v) for v in range(1, 9)])
        else:
            if version < 1 or version > 8:
                raise ValueError(f"UUID version {version} not supported. Use 1-8.")
            return _uuid(version)

    # ================================
    # Number Patterns
    # ================================

    @staticmethod
    def integer() -> Scrive:
        """
        Match integer number pattern.

        Returns:
            Scrive pattern matching integers (with optional sign)

        Example:
            >>> S.integer()  # Matches: 42, -17, +123
        """
        sign = S.char("+-").maybe()
        digits = S.digit().one_or_more()
        return sign + digits
        
    @staticmethod
    def uint() -> Scrive:
        """
        Match unsigned integer number pattern.

        Returns:
            Scrive pattern matching unsigned integers

        Example:
            >>> S.uint()  # Matches: 42, 17, 123
        """
        digits = S.digit().one_or_more()
        return digits
        
    @staticmethod
    def decimal() -> Scrive:
        """
        Match decimal number pattern.

        Returns:
            Scrive pattern matching decimal numbers

        Example:
            >>> S.decimal()  # Matches: 3.14, -2.5, +0.123
        """
        sign = S.char("+-").maybe()
        integer_part = S.digit().one_or_more()
        decimal_part = (S.literal(".") + S.digit().one_or_more()).maybe()
        return sign + integer_part + decimal_part
        
    @staticmethod
    def float() -> Scrive:
        """
        Match decimal number pattern.

        Returns:
            Scrive pattern matching decimal numbers

        Example:
            >>> S.float()  # Matches: 3.14, -2.5, +0.123
        """
        return S.decimal()
        
    @staticmethod
    def ufloat() -> Scrive:
        """
        Match unsigned decimal number pattern.

        Returns:
            Scrive pattern matching unsigned decimal numbers

        Example:
            >>> S.ufloat()  # Matches: 3.14, 2.5, 0.123
        """
        integer_part = S.digit().one_or_more()
        decimal_part = (S.literal(".") + S.digit().one_or_more()).maybe()
        return integer_part + decimal_part
        
    @staticmethod
    def udecimal() -> Scrive:
        """
        Match unsigned decimal number pattern.

        Returns:
            Scrive pattern matching unsigned decimal numbers

        Example:
            >>> S.udecimal()  # Matches: 3.14, 2.5, 0.123
        """
        return S.ufloat()
        
    @staticmethod
    def number_range(min_val: int, max_val: int) -> Scrive:
        """
        Match numbers in a specific range.

        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)

        Returns:
            Scrive pattern matching numbers in range

        Example:
            >>> S.number_range(1, 255)  # IPv4 octet range
        """
        from .macros import decimal_range

        return decimal_range(min_val, max_val)

    # ================================
    # Factory Methods
    # ================================

    @staticmethod
    def empty() -> Scrive:
        """
        Create empty Scrive pattern for building complex patterns.

        Returns:
            Empty Scrive instance

        Example:
            >>> pattern = S.empty().literal("hello").space().digit().times(3)
        """
        return Scrive()

    @staticmethod
    def from_pattern(pattern: Union[Scrive, str], flags: int = 0) -> Scrive:
        """
        Create Scrive from existing pattern or string.

        Args:
            pattern: Existing pattern or string
            flags: Regex flags to apply

        Returns:
            Scrive instance

        Example:
            >>> S.from_pattern(r"\\d+", re.IGNORECASE)
        """
        if isinstance(pattern, Scrive):
            result = pattern.copy()
            result._flags |= flags
            return result
        else:
            return Scrive(str(pattern), flags)


# Note: Method delegation to Scrive class is handled in __init__.py to avoid circular imports
