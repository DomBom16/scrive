"""
Comprehensive tests for Scrive unified API.

Tests both the S factory class and enhanced Scrive methods to ensure
the unified API works correctly and maintains backward compatibility.
"""

import re

import pytest

from scrive import S, Scrive


class TestSFactoryBasics:
    """Test basic S factory methods"""

    def test_literal(self):
        pattern = S.literal("hello")
        assert str(pattern) == "hello"
        assert pattern.test("hello")
        assert not pattern.test("world")

    def test_raw(self):
        pattern = S.raw(r"\d+")
        assert str(pattern) == r"\d+"
        assert pattern.test("123")
        assert not pattern.test("abc")

    def test_char_single(self):
        pattern = S.char("a")
        assert str(pattern) == "a"
        assert pattern.test("a")
        assert not pattern.test("b")

    def test_char_multiple(self):
        pattern = S.char("a", "e", "i", "o", "u")
        assert str(pattern) == "[aeiou]"
        assert pattern.test("a")
        assert pattern.test("i")
        assert not pattern.test("b")

    def test_char_from_string(self):
        pattern = S.char("aeiou")
        assert str(pattern) == "[aeiou]"
        assert pattern.test("e")
        assert not pattern.test("x")

    def test_char_range(self):
        pattern = S.char_range("a", "z")
        assert str(pattern) == "[a-z]"
        assert pattern.test("m")
        assert not pattern.test("Z")

    def test_none_of(self):
        pattern = S.not_char("aeiou")
        assert str(pattern) == "[^aeiou]"
        assert pattern.test("b")
        assert not pattern.test("a")


class TestSCharacterClasses:
    """Test S factory character class methods"""

    def test_any_char(self):
        pattern = S.any_char()
        assert str(pattern) == "."
        assert pattern.test("a")
        assert pattern.test("1")
        assert pattern.test("!")

    def test_digit(self):
        pattern = S.digit()
        assert str(pattern) == "\\d"
        assert pattern.test("5")
        assert not pattern.test("a")

    def test_letter(self):
        pattern = S.letter()
        assert str(pattern) == "[a-zA-Z]"
        assert pattern.test("a")
        assert pattern.test("Z")
        assert not pattern.test("1")

    def test_word(self):
        pattern = S.word()
        assert str(pattern) == "\\w"
        assert pattern.test("a")
        assert pattern.test("1")
        assert pattern.test("_")
        assert not pattern.test("!")

    def test_whitespace(self):
        pattern = S.whitespace()
        assert str(pattern) == "\\s"
        assert pattern.test(" ")
        assert pattern.test("\t")
        assert not pattern.test("a")

    def test_lowercase(self):
        pattern = S.lowercase()
        assert str(pattern) == "[a-z]"
        assert pattern.test("a")
        assert not pattern.test("A")

    def test_uppercase(self):
        pattern = S.uppercase()
        assert str(pattern) == "[A-Z]"
        assert pattern.test("A")
        assert not pattern.test("a")

    def test_alphanumeric(self):
        pattern = S.alphanumeric()
        assert str(pattern) == "[a-zA-Z0-9]"
        assert pattern.test("a")
        assert pattern.test("1")
        assert not pattern.test("!")

    def test_hexadecimal(self):
        pattern = S.hex()
        assert str(pattern) == "[0-9a-fA-F]"
        assert pattern.test("a")
        assert pattern.test("F")
        assert pattern.test("9")
        assert not pattern.test("g")

    def test_negated_classes(self):
        assert str(S.not_digit()) == "\\D"
        assert str(S.not_word()) == "\\W"
        assert str(S.not_whitespace()) == "\\S"

    def test_special_chars(self):
        assert str(S.tab()) == "\\t"
        assert str(S.newline()) == "\\n"
        assert str(S.carriage_return()) == "\\r"
        assert str(S.space()) == " "


class TestQuantifiers:
    """Test quantifier methods"""

    def test_maybe(self):
        pattern = S.literal("s").maybe().anchor_string()
        assert str(S.literal("s").maybe()) == "s?"
        assert pattern.test("")
        assert pattern.test("s")
        assert not pattern.test("ss")

    def test_one_or_more(self):
        pattern = S.digit().one_or_more()
        assert str(pattern) == "\\d+"
        assert pattern.test("1")
        assert pattern.test("123")
        assert not pattern.test("")

    def test_zero_or_more(self):
        pattern = S.letter().zero_or_more()
        assert str(pattern) == "[a-zA-Z]*"
        assert pattern.test("")
        assert pattern.test("abc")

    def test_times_exact(self):
        pattern = S.digit().times(3).anchor_string()
        assert str(S.digit().times(3)) == "\\d{3}"
        assert pattern.test("123")
        assert not pattern.test("12")
        assert not pattern.test("1234")

    def test_times_range(self):
        pattern = S.letter().times(2, 4).anchor_string()
        assert str(S.letter().times(2, 4)) == "[a-zA-Z]{2,4}"
        assert pattern.test("ab")
        assert pattern.test("abcd")
        assert not pattern.test("a")
        assert not pattern.test("abcde")

    def test_at_least(self):
        pattern = S.digit().at_least(2)
        assert str(pattern) == "\\d{2,}"
        assert pattern.test("12")
        assert pattern.test("123456")
        assert not pattern.test("1")

    def test_at_most(self):
        pattern = S.letter().at_most(3)
        assert str(pattern) == "[a-zA-Z]{,3}"
        assert pattern.test("")
        assert pattern.test("abc")

    def test_between(self):
        pattern = S.word().between(2, 5)
        assert str(pattern) == "\\w{2,5}"
        assert pattern.test("ab")
        assert pattern.test("abcde")
        assert not pattern.test("a")

    def test_lazy_quantifiers(self):
        pattern = S.any_char().maybe_lazy()
        assert str(pattern) == ".??"

        pattern = S.any_char().one_or_more_lazy()
        assert str(pattern) == ".+?"

        pattern = S.any_char().zero_or_more_lazy()
        assert str(pattern) == ".*?"


class TestAnchorsAndBoundaries:
    """Test anchor and boundary methods"""

    def test_string_anchors(self):
        pattern = S.literal("hello").anchor_string()
        assert str(pattern) == "^hello$"
        assert pattern.test("hello")
        assert not pattern.test("hello world")

    def test_individual_anchors(self):
        start = S.literal("hello").start_of_string()
        assert str(start) == "^hello"

        end = S.literal("hello").end_of_string()
        assert str(end) == "hello$"

    def test_line_anchors(self):
        pattern = S.literal("hello").anchor_line()
        assert pattern.flags & re.MULTILINE
        assert str(pattern) == "^hello$"

    def test_word_boundaries(self):
        pattern = S.literal("cat").word_boundary()
        assert str(pattern) == "\\bcat\\b"
        assert pattern.test("cat")
        assert pattern.test("a cat here")
        assert not pattern.test("catch")

    def test_boundary_factories(self):
        wb = S.word_boundary()
        assert str(wb) == "\\b"

        nwb = S.non_word_boundary()
        assert str(nwb) == "\\B"


class TestLookaround:
    """Test lookahead and lookbehind assertions"""

    def test_followed_by(self):
        pattern = S.literal("hello").followed_by(S.space())
        assert "(?= )" in str(pattern)
        assert pattern.test("hello world")
        assert not pattern.test("hello!")

    def test_not_followed_by(self):
        pattern = S.literal("hello").not_followed_by(S.space())
        assert "(?! )" in str(pattern)
        assert pattern.test("hello!")
        assert not pattern.test("hello world")

    def test_preceded_by(self):
        pattern = S.literal("world").preceded_by(S.literal("hello "))
        assert "(?<=hello\\ )" in str(pattern)

    def test_not_preceded_by(self):
        pattern = S.literal("world").not_preceded_by(S.literal("hello "))
        assert "(?<!hello\\ )" in str(pattern)


class TestGrouping:
    """Test grouping and capturing methods"""

    def test_group_unnamed(self):
        pattern = S.group(S.digit().one_or_more())
        assert str(pattern) == "(\\d+)"

    def test_group_named(self):
        pattern = S.group(S.digit().one_or_more(), "number")
        assert str(pattern) == "(?P<number>\\d+)"

    def test_non_capturing_group(self):
        pattern = S.non_capturing_group(S.choice("cat", "dog"))
        assert str(pattern).startswith("(?:")

    def test_references(self):
        named_ref = S.reference("word")
        assert str(named_ref) == "(?P=word)"

        numbered_ref = S.reference(1)
        assert str(numbered_ref) == "\\1"

    def test_instance_grouping_methods(self):
        pattern = S.digit().one_or_more().group("number")
        assert "(?P<number>" in str(pattern)

        pattern = S.digit().one_or_more().capture("number")
        assert "(?P<number>" in str(pattern)

        pattern = S.digit().one_or_more().named("number")
        assert "(?P<number>" in str(pattern)


class TestCombinators:
    """Test pattern combination methods"""

    def test_choice(self):
        pattern = S.choice("cat", "dog", "bird")
        assert pattern.test("cat")
        assert pattern.test("dog")
        assert pattern.test("bird")
        assert not pattern.test("fish")

    def test_choice_optimization(self):
        # Single characters should become character class
        pattern = S.choice("a", "e", "i")
        assert "[" in str(pattern) and "]" in str(pattern)

    def test_sequence(self):
        pattern = S.sequence(S.literal("hello"), S.space(), S.literal("world"))
        assert str(pattern) == "hello world"
        assert pattern.test("hello world")

    def test_chaining_then(self):
        pattern = S.literal("hello").then(S.space()).then(S.literal("world"))
        assert str(pattern) == "hello world"

    def test_or_else_chaining(self):
        pattern = S.literal("cat").or_else("dog", "bird")
        assert pattern.test("cat")
        assert pattern.test("dog")
        assert not pattern.test("fish")

    def test_separated_by(self):
        pattern = S.digit().separated_by(S.literal("."), 4)
        # Should match patterns like "1.2.3.4"
        result_str = str(pattern)
        assert "." in result_str
        # Test that it creates the right structure
        test_pattern = S.digit().separated_by(S.literal("-"), 3)
        assert test_pattern.test("1-2-3")


class TestCommonPatterns:
    """Test built-in common patterns"""

    def test_email(self):
        pattern = S.email()
        assert pattern.test("user@example.com")
        assert pattern.test("test.email@domain.co.uk")
        assert not pattern.test("invalid.email")

    def test_url(self):
        pattern = S.url()
        assert pattern.test("https://example.com")
        assert pattern.test("http://test.domain.org/path")

    def test_ipv4(self):
        pattern = S.ipv4().anchor_string()
        assert pattern.test("192.168.1.1")
        assert pattern.test("127.0.0.1")
        assert not pattern.test("256.1.1.1")  # Invalid octet

    def test_phone(self):
        pattern = S.phone()
        # Test various phone formats
        assert pattern.test("123-456-7890")
        assert pattern.test("(123) 456-7890")

    def test_uuid(self):
        uuid_any = S.uuid()
        uuid_v4 = S.uuid(4)

        # Test with a valid UUID v4
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        assert uuid_any.test(test_uuid)

    def test_number_patterns(self):
        integer = S.integer()
        assert integer.test("123")
        assert integer.test("-456")
        assert integer.test("+789")

        decimal = S.decimal()
        assert decimal.test("123.45")
        assert decimal.test("-67.89")

        range_pattern = S.number_range(1, 100)
        assert range_pattern.test("50")
        assert range_pattern.test("1")
        assert range_pattern.test("100")


class TestFlags:
    """Test flag methods"""

    def test_ignore_case(self):
        pattern = S.literal("hello").ignore_case()
        assert pattern.flags & re.IGNORECASE
        assert pattern.test("HELLO")
        assert pattern.test("Hello")

    def test_case_insensitive_alias(self):
        pattern = S.literal("hello").case_insensitive()
        assert pattern.flags & re.IGNORECASE

    def test_multiline(self):
        pattern = S.literal("hello").multiline()
        assert pattern.flags & re.MULTILINE

    def test_dotall(self):
        pattern = S.any_char().dot_all()
        assert pattern.flags & re.DOTALL

    def test_verbose(self):
        pattern = S.literal("hello").verbose()
        assert pattern.flags & re.VERBOSE


class TestTestingMethods:
    """Test pattern testing and compilation methods"""

    def test_compilation(self):
        pattern = S.digit().one_or_more()
        compiled = pattern.compile()
        assert isinstance(compiled, re.Pattern)

    def test_test_method(self):
        pattern = S.literal("hello")
        assert pattern.test("hello world")  # substring match
        assert not pattern.test("hi world")

    def test_exact_match(self):
        pattern = S.literal("hello").anchor_string()
        assert pattern.exact_match("hello")
        assert not pattern.exact_match("hello world")

    def test_find_all(self):
        pattern = S.digit().one_or_more()
        text = "I have 123 apples and 456 oranges"
        matches = pattern.find_all(text)
        assert "123" in matches
        assert "456" in matches

    def test_split(self):
        pattern = S.literal(",")
        result = pattern.split("a,b,c")
        assert len(result) >= 3

    def test_replace(self):
        pattern = S.digit().one_or_more()
        result = pattern.replace("I have 123 items", "XXX")
        assert "XXX" in result
        assert "123" not in result


class TestFactoryMethods:
    """Test S factory utility methods"""

    def test_empty(self):
        pattern = S.empty()
        assert str(pattern) == ""

    def test_from_pattern_string(self):
        pattern = S.from_pattern("hello", re.IGNORECASE)
        assert str(pattern) == "hello"
        assert pattern.flags & re.IGNORECASE

    def test_from_pattern_scrive(self):
        original = S.digit()
        pattern = S.from_pattern(original, re.MULTILINE)
        assert str(pattern) == "\\d"
        assert pattern.flags & re.MULTILINE


class TestMethodDelegation:
    """Test that S methods are available on Scrive instances"""

    def test_scrive_has_s_methods(self):
        # Test that Scrive class has factory methods
        assert hasattr(Scrive, "digit")
        assert hasattr(Scrive, "literal")
        assert hasattr(Scrive, "email")

    def test_scrive_static_methods_work(self):
        pattern = Scrive.digit().one_or_more()
        assert str(pattern) == "\\d+"

        email = Scrive.email()
        assert email.test("user@example.com")


class TestEnhancedChaining:
    """Test enhanced chaining methods"""

    def test_then_alias(self):
        pattern = S.literal("hello").then(S.space(), S.literal("world"))
        assert str(pattern) == "hello world"

    def test_optional_alias(self):
        pattern = S.literal("s").optional()
        assert str(pattern) == "s?"

    def test_repeat_alias(self):
        pattern = S.digit().repeat(3)
        assert str(pattern) == "\\d{3}"


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_choice_empty(self):
        with pytest.raises(ValueError):
            S.choice()

    def test_times_negative(self):
        with pytest.raises(ValueError):
            S.digit().times(-1)

    def test_invalid_uuid_version(self):
        with pytest.raises(ValueError):
            S.uuid(99)

    def test_separated_by_zero_count(self):
        with pytest.raises(ValueError):
            S.digit().separated_by(S.literal("."), 0)


class TestComplexPatterns:
    """Test complex real-world patterns"""

    def test_username_validation(self):
        # 3-20 chars, starts with letter, followed by word chars
        username = S.letter().then(S.word().times(2, 19)).anchor_string()

        assert username.test("user123")
        assert username.test("abc")
        assert not username.test("a")  # too short
        assert not username.test("123user")  # starts with digit

    def test_password_validation(self):
        # At least 8 chars with uppercase, lowercase, digit
        # Use lookaheads at the start to check requirements
        password = (
            S.start_of_string()
            .then(S.raw("(?=.*[A-Z])"))  # Has uppercase
            .then(S.raw("(?=.*[a-z])"))  # Has lowercase
            .then(S.raw("(?=.*\\d)"))  # Has digit
            .then(S.any_char().at_least(8))  # At least 8 chars
            .then(S.end_of_string())
        )

        assert password.test("Password123")
        assert not password.test("password")  # no uppercase
        assert not password.test("PASSWORD123")  # no lowercase
        assert not password.test("Password")  # no digit

    def test_csv_parsing(self):
        # Simple CSV field matching
        quoted_field = (
            S.literal('"').then(S.not_char('"').zero_or_more()).then(S.literal('"'))
        )
        unquoted_field = S.not_char('",\n').zero_or_more()
        csv_field = S.choice(quoted_field, unquoted_field)

        assert csv_field.test('"quoted field"')
        assert csv_field.test("unquoted")
        assert csv_field.test("")

    def test_log_timestamp(self):
        # Common log timestamp: [DD/Mon/YYYY:HH:MM:SS +ZZZZ]
        day = S.digit().times(2)
        month = S.choice(
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        )
        year = S.digit().times(4)
        hour = S.digit().times(2)
        minute = S.digit().times(2)
        second = S.digit().times(2)
        timezone = S.char("+-").then(S.digit().times(4))

        timestamp = (
            S.literal("[")
            .then(day)
            .then(S.literal("/"))
            .then(month)
            .then(S.literal("/"))
            .then(year)
            .then(S.literal(":"))
            .then(hour)
            .then(S.literal(":"))
            .then(minute)
            .then(S.literal(":"))
            .then(second)
            .then(S.space())
            .then(timezone)
            .then(S.literal("]"))
        )

        assert timestamp.test("[25/Dec/2023:10:30:45 +0000]")


class TestBackwardCompatibility:
    """Ensure backward compatibility with legacy API"""

    def test_legacy_imports_still_work(self):
        # These should still be importable from the unified API
        from scrive import email

        pattern = email()
        assert pattern.test("user@example.com")

    def test_mixed_usage(self):
        # Should be able to mix S factory with common patterns
        from scrive import email

        pattern = S.digit().then(S.literal("-")).then(S.digit())
        email_pattern = email()
        assert "-" in str(pattern)
        assert email_pattern.test("test@example.com")


if __name__ == "__main__":
    pytest.main([__file__])
