#!/usr/bin/env python3
"""
Enhanced Scrive Examples - Showcasing New Features

This file demonstrates all the new enhancement features added to Scrive,
including raw regex support, negation, chained replacements, Unicode support,
custom validators, pattern templating, and more.
"""

from scrive import (
    Scrive,
    any_char,
    case_insensitive,
    case_sensitive,
    char,
    digit,
    email,
    exactly,
    invert,
    letter,
    one_of,
    raw,
    ref,
    template,
    whitespace,
    word_char,
    separated_by,
)


def demo_raw_regex_support():
    """Demonstrate raw regex injection for complex patterns."""
    print("=== Raw Regex Support ===")

    # Mix Scrive patterns with raw regex for complex cases
    log_pattern = (
        exactly("[")
        + raw(r"\d{4}-\d{2}-\d{2}")  # ISO date format
        + exactly(" ")
        + raw(r"\d{2}:\d{2}:\d{2}")  # Time format
        + exactly("] ")
        + word_char().one_or_more()
        + raw(r"\s+")  # Flexible whitespace
        + any_char().one_or_more()
    )

    test_log = "[2023-12-25 14:30:45] INFO User logged in successfully"
    print(f"Pattern: {log_pattern.pattern}")
    print(f"Matches log: {log_pattern.test(test_log)}")

    # Raw regex for lookbehind/lookahead that's hard to express in Scrive
    password_strength = (
        any_char()
        + raw(r"(?=.*[a-z])")  # Must contain lowercase
        + raw(r"(?=.*[A-Z])")  # Must contain uppercase
        + raw(r"(?=.*\d)")  # Must contain digit
        + raw(r"(?=.*[@$!%*?&])")  # Must contain special char
    ).between(8, 128)

    print(f"\nPassword pattern: {password_strength.pattern}")
    print(f"Strong password 'Test123!': {password_strength.exact_match('Test123!')}")
    print(f"Weak password 'password': {password_strength.exact_match('password')}")


def demo_pattern_negation():
    """Demonstrate pattern negation and inversion."""
    print("\n=== Pattern Negation ===")

    # Character class inversion
    vowels = char("aeiouAEIOU")
    consonants = invert(vowels)

    print(f"Vowels pattern: {vowels.pattern}")
    print(f"Consonants pattern: {consonants.pattern}")
    print(f"'b' matches consonants: {consonants.test('b')}")
    print(f"'a' matches consonants: {consonants.test('a')}")

    # Negating complex patterns
    number_pattern = digit().one_or_more()
    not_number = invert(number_pattern)

    print(f"\nNot number pattern: {not_number.pattern}")
    print(f"Text 'hello' matches not-number: {not_number.test('hello')}")

    # Real-world example: matching non-email text
    email_pattern = email()
    non_email = invert(email_pattern)

    print(f"\nNon-email pattern: {non_email.pattern}")


def demo_inline_comments():
    """Demonstrate inline comments for readable regex."""
    print("\n=== Inline Comments ===")

    # Complex pattern with comments
    credit_card_pattern = (
        digit().times(4).verbose().comment("First 4 digits")
        + raw(r"[\s-]?").comment("Optional separator")
        + digit().times(4).comment("Second group")
        + raw(r"[\s-]?").comment("Optional separator")
        + digit().times(4).comment("Third group")
        + raw(r"[\s-]?").comment("Optional separator")
        + digit().times(4).comment("Last 4 digits")
    )

    print(f"Commented pattern:\n{credit_card_pattern.pattern}")

    test_cards = ["1234 5678 9012 3456", "1234-5678-9012-3456", "1234567890123456"]

    for card in test_cards:
        print(f"'{card}' matches: {credit_card_pattern.test(card)}")


def demo_numbered_backreferences():
    """Demonstrate numbered group backreferences."""
    print("\n=== Numbered Backreferences ===")

    # Palindrome detector using backreferences
    palindrome_4 = (
        word_char().group()  # Group 1
        + word_char().group()  # Group 2
        + ref(2)  # Reference to group 2
        + ref(1)  # Reference to group 1
    )

    print(f"4-char palindrome pattern: {palindrome_4.pattern}")

    test_words = ["abba", "deed", "test", "race", "noon"]
    for word in test_words:
        print(f"'{word}' is palindrome: {palindrome_4.exact_match(word)}")

    # HTML tag matching
    html_tag = (
        exactly("<")
        + word_char().one_or_more().group()  # Tag name in group 1
        + (whitespace().one_or_more() + any_char().zero_or_more()).maybe()  # Attributes
        + exactly(">")
        + any_char().zero_or_more()  # Content
        + exactly("</")
        + ref(1)  # Same tag name
        + exactly(">")
    )

    print(f"\nHTML tag pattern: {html_tag.pattern}")

    html_tests = [
        "<div>content</div>",
        "<p class='test'>text</p>",
        "<div>content</span>",  # Mismatched
    ]

    for html in html_tests:
        print(f"'{html}' is valid: {html_tag.test(html)}")


def demo_case_transformation():
    """Demonstrate case transformation groups."""
    print("\n=== Case Transformation ===")

    # Mixed case requirements
    username_pattern = case_insensitive(
        letter().between(3, 20)
    ) + case_sensitive(  # Username can be any case
        digit().one_or_more().maybe()
    )  # Optional numbers (case sensitive)

    print(f"Username pattern: {username_pattern.pattern}")

    usernames = ["JohnDoe123", "janedoe", "ADMIN999", "user"]
    for username in usernames:
        print(f"'{username}' valid: {username_pattern.exact_match(username)}")


def demo_pattern_templating():
    """Demonstrate pattern templating with variables."""
    print("\n=== Pattern Templating ===")

    # SQL query template
    sql_template = Scrive(
        "SELECT {fields} FROM {table} WHERE {condition} ORDER BY {sort_field}"
    )

    # Fill with patterns
    sql_pattern = template(
        sql_template,
        fields=separated_by(word_char().one_or_more(), exactly(", "), 3),
        table=word_char().one_or_more(),
        condition=word_char().one_or_more() + exactly(" = ") + any_char().one_or_more(),
        sort_field=word_char().one_or_more(),
    )

    print(f"SQL template pattern: {sql_pattern.pattern}")

    test_sql = "SELECT name, email, age FROM users WHERE status = active ORDER BY name"
    print(f"Matches SQL: {sql_pattern.test(test_sql)}")

    # Configuration file template
    config_template = Scrive("{section}.{key} = {value}")

    config_pattern = template(
        config_template,
        section=word_char().one_or_more(),
        key=word_char().one_or_more(),
        value=any_char().one_or_more(),
    )

    print(f"\nConfig pattern: {config_pattern.pattern}")

    config_lines = [
        "database.host = localhost",
        "server.port = 8080",
        "cache.enabled = true",
    ]

    for line in config_lines:
        print(f"'{line}' matches config: {config_pattern.test(line)}")


def demo_advanced_alternation():
    """Demonstrate advanced alternation with | operator."""
    print("\n=== Advanced Alternation ===")

    # Protocol matching with alternation
    protocol = exactly("http") | exactly("https") | exactly("ftp") | exactly("ftps")

    # Or using one_of for cleaner syntax
    protocol_clean = one_of("http", "https", "ftp", "ftps")

    print(f"Protocol pattern: {protocol.pattern}")
    print(f"Clean protocol pattern: {protocol_clean.pattern}")

    test_protocols = ["http", "https", "ftp", "ssh", "ftps"]
    for proto in test_protocols:
        print(f"'{proto}' matches: {protocol.test(proto)}")

    # File extension matching
    image_ext = one_of("jpg", "jpeg", "png", "gif", "webp", "svg")
    document_ext = one_of("pdf", "doc", "docx", "txt", "md")

    file_pattern = word_char().one_or_more() + exactly(".") + (image_ext | document_ext)

    print(f"\nFile pattern: {file_pattern.pattern}")

    test_files = ["image.jpg", "document.pdf", "script.py", "photo.png"]
    for file_test in test_files:
        print(f"'{file_test}' matches: {file_pattern.test(file_test)}")


def main():
    """Run all enhancement feature demonstrations."""
    print("Scrive Enhanced Features Demonstration")
    print("=" * 50)

    demo_raw_regex_support()
    demo_pattern_negation()
    demo_inline_comments()
    demo_numbered_backreferences()
    demo_case_transformation()
    demo_pattern_templating()
    demo_advanced_alternation()

    print("\n" + "=" * 50)
    print("All enhancement features demonstrated!")
    print("Check the source code for implementation details.")


if __name__ == "__main__":
    main()
