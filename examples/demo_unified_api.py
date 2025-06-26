#!/usr/bin/env python3
"""
Scrive Unified API - Final Demonstration

This script demonstrates the power and elegance of the new unified Scrive API.
Shows real-world examples and comparisons with the old fragmented approach.

Run with: python demo_unified_api.py
"""

import sys

# Add the current directory to Python path to import scrive
sys.path.insert(0, ".")

from scrive import S


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print("=" * 60)


def print_example(description, pattern, test_cases):
    """Print an example with test cases"""
    print(f"\n{description}")
    print(f"Pattern: {pattern}")
    print(f"Regex:   {pattern}")

    for test_input, expected in test_cases:
        result = pattern.test(test_input)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{test_input}' -> {result}")


def demo_basic_usage():
    """Demonstrate basic unified API usage"""
    print_section("Basic Usage - Single Import, Fluent API")

    print("# Single import gives you everything:")
    print("from scrive import S")

    print("\n# Simple patterns with fluent chaining:")

    # Vowels
    vowels = S.char("aeiou")
    print_example(
        "1. Character classes - vowels",
        vowels,
        [("a", True), ("x", False), ("e", True)],
    )

    # Digits with quantifiers
    numbers = S.digit().one_or_more()
    print_example(
        "2. Quantifiers - one or more digits",
        numbers,
        [("123", True), ("abc", False), ("12abc", True)],
    )

    # Anchored email
    email = S.email().anchor_string()
    print_example(
        "3. Built-in patterns - email validation",
        email,
        [
            ("user@example.com", True),
            ("invalid.email", False),
            ("test@domain.co.uk", True),
            ("spaces in@email.com", False),
        ],
    )


def demo_pattern_building():
    """Demonstrate advanced pattern building"""
    print_section("Advanced Pattern Building")

    # IPv4 address
    ipv4 = S.number_range(0, 255).separated_by(S.literal("."), 4).anchor_string()
    print_example(
        "1. IPv4 Address - number ranges with separators",
        ipv4,
        [
            ("192.168.1.1", True),
            ("127.0.0.1", True),
            ("256.1.1.1", False),
            ("192.168.1", False),
        ],
    )

    # Phone number variations - use the built-in phone pattern
    phone = S.phone().anchor_string()

    print_example(
        "2. Phone Numbers - multiple formats with choice",
        phone,
        [
            ("(555) 123-4567", True),
            ("555-123-4567", True),
            ("+1 555 123 4567", True),
            ("555.123.4567", True),
            ("abc-def-ghij", False),
        ],
    )


def demo_real_world_patterns():
    """Demonstrate real-world validation patterns"""
    print_section("Real-World Validation Patterns")

    # Username validation: 3-20 chars, starts with letter
    username = S.letter().then(S.word().times(2, 19)).anchor_string()
    print_example(
        "1. Username - 3-20 chars, starts with letter",
        username,
        [
            ("user123", True),
            ("admin", True),
            ("abc", True),
            ("a", False),  # too short
            ("123user", False),  # starts with digit
            ("user_name_that_is_way_too_long_for_validation", False),  # too long
        ],
    )

    # Password requirements
    password = (
        S.start_of_string()
        .then(S.raw("(?=.*[A-Z])"))  # Has uppercase
        .then(S.raw("(?=.*[a-z])"))  # Has lowercase
        .then(S.raw("(?=.*\\d)"))  # Has digit
        .then(S.any_char().at_least(8))  # At least 8 chars
        .then(S.end_of_string())
    )

    print_example(
        "2. Password - 8+ chars with upper, lower, digit",
        password,
        [
            ("Password123", True),
            ("password", False),  # no uppercase
            ("PASSWORD123", False),  # no lowercase
            ("Password", False),  # no digit
            ("Pass1", False),  # too short
        ],
    )

    # URL validation
    url = S.url()
    print_example(
        "3. URL - comprehensive URL matching",
        url,
        [
            ("https://example.com", True),
            ("http://test.domain.org/path", True),
            ("ftp://files.example.com/file.txt", True),
            ("not-a-url", False),
            ("www.example.com", False),  # missing protocol
        ],
    )


def demo_data_extraction():
    """Demonstrate data extraction patterns"""
    print_section("Data Extraction Patterns")

    # Extract hashtags
    hashtag = S.literal("#").then(S.word().one_or_more().group("tag"))

    text = "Love #python and #regex for #coding! #awesome"
    compiled_pattern = hashtag.compile()
    matches = [match.group("tag") for match in compiled_pattern.finditer(text)]

    print("1. Hashtag Extraction")
    print(f"Pattern: {hashtag}")
    print(f"Text: '{text}'")
    print(f"Hashtags found: {matches}")

    # Extract version numbers
    version = S.sequence(
        S.char("v", "V").maybe(),
        S.digit().one_or_more().group("major"),
        S.literal("."),
        S.digit().one_or_more().group("minor"),
        S.literal(".").then(S.digit().one_or_more().group("patch")).maybe(),
        S.char(".", "-", "_", "").then(S.word().one_or_more().group("type")).maybe(),
    )

    version_texts = ["v1.2.3", "version 2.0", "app-3.1.4-beta"]
    print("\n2. Version Number Extraction")
    print(f"Pattern: {version}")

    for text in version_texts:
        match = version.search(text)
        if match:
            groups = match.groupdict()
            print(f"  '{text}' -> {groups}")
        else:
            print(f"  '{text}' -> No match")


def demo_csv_parsing():
    """Demonstrate CSV parsing capabilities"""
    print_section("CSV Parsing")

    # CSV field with quoted and unquoted support
    quoted_field = (
        S.literal('"').then(S.not_char('"').zero_or_more()).then(S.literal('"'))
    )

    unquoted_field = S.not_char('",\n').one_or_more()

    csv_field = S.choice(quoted_field, unquoted_field)
    csv_row = csv_field.then(S.literal(",").then(csv_field).zero_or_more())

    csv_examples = [
        "name,age,city",
        '"John Doe",30,"New York"',
        "simple,field,test",
        '"field with, comma",42,normal',
    ]

    print("CSV Row Parser")
    print(f"Pattern: {csv_row}")

    for csv_line in csv_examples:
        if csv_row.test(csv_line):
            print(f"  ✓ '{csv_line}'")
        else:
            print(f"  ✗ '{csv_line}'")


def demo_log_parsing():
    """Demonstrate log parsing"""
    print_section("Log Parsing")

    # Apache log format
    apache_log = S.sequence(
        S.ipv4().group("ip"),  # IP address
        S.literal(" - - "),  # User identifier and authentication
        S.literal("[")
        .then(  # Timestamp
            S.not_char("]").one_or_more().group("timestamp")
        )
        .then(S.literal("] ")),
        S.literal('"')
        .then(  # Request
            S.not_char('"').one_or_more().group("request")
        )
        .then(S.literal('" ')),
        S.digit().one_or_more().group("status"),  # Status code
        S.literal(" "),
        S.digit().one_or_more().group("size"),  # Response size
    )

    log_line = '192.168.1.1 - - [25/Dec/2023:10:30:45 +0000] "GET /index.html HTTP/1.1" 200 1234'

    print("Apache Log Parser")
    print(f"Pattern: {apache_log}")
    print(f"Log line: {log_line}")

    match = apache_log.search(log_line)
    if match:
        groups = match.groupdict()
        print("Extracted fields:")
        for field, value in groups.items():
            print(f"  {field}: {value}")
    else:
        print("No match found")


def demo_optimization():
    """Demonstrate pattern optimization"""
    print_section("Pattern Optimization")

    print("Scrive automatically optimizes patterns for better performance:")

    # Character class optimization
    manual_chars = S.char("a", "b", "c", "d", "e")
    print("\n1. Character ranges: S.char('a', 'b', 'c', 'd', 'e')")
    print(f"   Optimized to: {manual_chars}")

    # Choice optimization
    digit_choice = S.choice("1", "2", "3", "4", "5")
    print("\n2. Digit choices: S.choice('1', '2', '3', '4', '5')")
    print(f"   Optimized to: {digit_choice}")

    # Number range optimization
    ip_octet = S.number_range(0, 255)
    print("\n3. Number ranges: S.number_range(0, 255)")
    print(f"   Optimized to: {ip_octet}")


def demo_comparison():
    """Compare old vs new API"""
    print_section("Old vs New API Comparison")

    print("OLD API (fragmented, hard to discover):")
    print("""
    from scrive import digit, exactly, one_or_more, separated_by
    from scrive.patterns import email
    from scrive.anchors import start_of_string, end_of_string

    # IPv4 pattern - verbose and hard to read
    ipv4 = separated_by(digit().between(1, 3), exactly("."), 4)
    ipv4 = start_of_string() + ipv4 + end_of_string()

    # Email validation - multiple imports needed
    email_pattern = email().start_of_string().end_of_string()
    """)

    print("\nNEW API (unified, discoverable):")
    print("""
    from scrive import S

    # IPv4 pattern - clear and readable
    ipv4 = S.number_range(0, 255).separated_by(S.literal("."), 4).anchor_string()
    # Or use built-in:
    ipv4 = S.ipv4().anchor_string()

    # Email validation - single import, clear method
    email_pattern = S.email().anchor_string()
    """)

    # Show actual results
    old_style = S.digit().between(1, 3)  # Simulate old approach
    new_style = S.number_range(0, 255)

    print("\nActual results:")
    print(f"Old approach: {old_style}")
    print(f"New approach: {new_style}")
    print("New is more precise and handles edge cases!")


def demo_fluent_chaining():
    """Demonstrate the power of fluent chaining"""
    print_section("Fluent Method Chaining")

    print("Build complex patterns step by step:")

    # Complex email with domain restrictions
    enterprise_email = (
        (
            S.word().one_or_more()  # Username
            + S.literal("@")  # @
            + S.choice("company", "enterprise")  # Allowed domains
            + S.literal(".")  # .
            + S.choice("com", "org", "net")  # TLD
        )
        .anchor_string()  # Exact match
        .ignore_case()  # Case insensitive
    )

    print_example(
        "Enterprise email validation (specific domains)",
        enterprise_email,
        [
            ("john@company.com", True),
            ("admin@enterprise.org", True),
            ("user@COMPANY.COM", True),  # case insensitive
            ("test@gmail.com", False),  # wrong domain
            ("admin@company.gov", False),  # wrong TLD
        ],
    )


def demo_testing_methods():
    """Demonstrate testing and compilation methods"""
    print_section("Testing and Compilation Methods")

    pattern = S.word().one_or_more()
    text = "Hello world 123"

    print(f"Pattern: {pattern}")
    print(f"Test text: '{text}'")
    print()

    # Different testing methods
    print(f"pattern.test(text)        -> {pattern.test(text)}")  # substring search
    print(f"pattern.match(text)       -> {pattern.match(text)}")  # from start
    print(f"pattern.search(text)      -> {pattern.search(text)}")  # search anywhere
    print(f"pattern.find_all(text)    -> {pattern.find_all(text)}")  # all matches

    # Exact matching
    exact_pattern = pattern.anchor_string()
    print("\nExact matching:")
    print(f"exact_pattern.test('hello')     -> {exact_pattern.test('hello')}")
    print(f"exact_pattern.test('hello!')    -> {exact_pattern.test('hello!')}")

    # Compilation
    compiled = pattern.compile()
    print(f"\nCompiled pattern type: {type(compiled)}")


def main():
    """Run all demonstrations"""
    print("🎯 Scrive Unified API - Complete Demonstration")
    print("=" * 60)
    print("This demo shows the power and elegance of the new unified Scrive API")

    try:
        demo_basic_usage()
        demo_pattern_building()
        demo_real_world_patterns()
        demo_data_extraction()
        demo_csv_parsing()
        demo_log_parsing()
        demo_optimization()
        demo_fluent_chaining()
        demo_testing_methods()
        demo_comparison()

        print_section("Summary")
        print("The unified Scrive API provides:")
        print("✓ Single import point (from scrive import S)")
        print("✓ Excellent discoverability through IDE autocomplete")
        print("✓ Fluent method chaining for readable patterns")
        print("✓ Built-in common patterns (email, URL, IPv4, etc.)")
        print("✓ Automatic pattern optimization")
        print("✓ Comprehensive testing methods")
        print("✓ Real-world pattern examples")
        print("✓ Full backward compatibility")
        print()
        print("🎉 Scrive: Making regex readable and maintainable!")
        print()
        print("Example patterns:")
        print(f"UUID (any version): {S.uuid()}")
        print(f"UUID v4: {S.uuid(4)}")
        print(f"Email: {S.email()}")
        print(f"IPv4: {S.ipv4()}")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the scrive directory")
        print("and that all modules are properly installed.")
        return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

    # Email validation with optional display name
    display_name = (
        S.literal('"')
        + S.not_char('"').zero_or_more().named("display_name")
        + S.literal('"')
        + S.space()
    )
    email = S.literal("<").maybe() + S.email().named("email") + S.literal(">").maybe()
    pattern = (display_name.maybe() + email).anchor_string()

    print(pattern)

    return 0


if __name__ == "__main__":
    exit(main())
