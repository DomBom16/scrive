"""
Scrive Unified API Examples

This file demonstrates the new unified API for Scrive, showing how the S factory
class makes pattern creation more discoverable and consistent.
"""

from scrive import S


def basic_patterns():
    """Basic pattern creation examples"""
    print("=== Basic Patterns ===")

    # Simple character matching
    vowels = S.char("aeiou")
    print(f"Vowels: {vowels}")
    print(f"Matches 'a': {vowels.test('a')}")
    print(f"Matches 'x': {vowels.test('x')}")

    # Character ranges
    lowercase = S.char_range("a", "z")
    print(f"Lowercase: {lowercase}")

    # Negation
    consonants = S.not_char("aeiou")
    print(f"Consonants: {consonants}")

    # Common classes
    word_char = S.word()
    digit = S.digit()
    whitespace = S.whitespace()
    print(f"Word char: {word_char}, Digit: {digit}, Whitespace: {whitespace}")


def quantifier_examples():
    """Examples of quantifier usage"""
    print("\n=== Quantifiers ===")

    # Basic quantifiers
    optional_s = S.literal("s").maybe()  # plurals
    one_or_more_digits = S.digit().one_or_more()
    zero_or_more_spaces = S.space().zero_or_more()

    print(f"Optional 's': {optional_s}")
    print(f"One or more digits: {one_or_more_digits}")
    print(f"Zero or more spaces: {zero_or_more_spaces}")

    # Exact counts
    three_digits = S.digit().times(3)
    two_to_four_letters = S.letter().times(2, 4)
    at_least_one_word = S.word().at_least(1)

    print(f"Exactly 3 digits: {three_digits}")
    print(f"2-4 letters: {two_to_four_letters}")
    print(f"At least 1 word char: {at_least_one_word}")


def anchoring_examples():
    """Examples of anchoring patterns"""
    print("\n=== Anchoring ===")

    # String anchors
    exact_hello = S.literal("hello").anchor_string()
    _starts_with_hi = S.literal("hi").start_of_string()
    _ends_with_bye = S.literal("bye").end_of_string()

    print(f"Exact 'hello': {exact_hello}")
    print(f"Test 'hello': {exact_hello.test('hello')}")
    print(f"Test 'hello world': {exact_hello.test('hello world')}")

    # Word boundaries
    whole_word_cat = S.literal("cat").word_boundary()
    print(f"Whole word 'cat': {whole_word_cat}")
    print(f"Test 'cat': {whole_word_cat.test('cat')}")
    print(f"Test 'catch': {whole_word_cat.test('catch')}")


def combination_examples():
    """Examples of combining patterns"""
    print("\n=== Pattern Combinations ===")

    # Choice/alternation
    pets = S.choice("cat", "dog", "bird")
    print(f"Pets: {pets}")
    print(f"Matches 'dog': {pets.test('dog')}")
    print(f"Matches 'fish': {pets.test('fish')}")

    # Sequence building
    greeting = (
        S.literal("Hello")
        .then(S.space())
        .then(S.word().one_or_more())
        .then(S.literal("!"))
    )
    print(f"Greeting: {greeting}")
    print(f"Matches 'Hello World!': {greeting.test('Hello World!')}")

    # Using sequence helper
    phone_pattern = S.sequence(
        S.digit().times(3),
        S.literal("-"),
        S.digit().times(3),
        S.literal("-"),
        S.digit().times(4),
    )
    print(f"Phone: {phone_pattern}")


def common_patterns():
    """Examples using built-in common patterns"""
    print("\n=== Common Patterns ===")

    # Built-in patterns
    email = S.email()
    url = S.url()
    ipv4 = S.ipv4()
    phone = S.phone()

    print(f"Email pattern: {email}")
    print(f"URL pattern: {url}")
    print(f"IPv4 pattern: {ipv4}")
    print(f"Phone pattern: {phone}")

    # Test email
    test_emails = ["user@example.com", "invalid.email", "test@test.co.uk"]
    for test_email in test_emails:
        print(f"'{test_email}' is valid email: {email.test(test_email)}")


def number_patterns():
    """Examples of number matching patterns"""
    print("\n=== Number Patterns ===")

    # Basic numbers
    integer = S.integer()
    decimal = S.decimal()

    print(f"Integer: {integer}")
    print(f"Decimal: {decimal}")

    # Number ranges
    percent = S.number_range(0, 100)  # 0-100 for percentages
    ipv4_octet = S.number_range(0, 255)  # IPv4 octet range

    print(f"Percentage (0-100): {percent}")
    print(f"IPv4 octet (0-255): {ipv4_octet}")

    # Test ranges
    test_values = ["50", "150", "300"]
    for val in test_values:
        print(f"'{val}' in 0-100 range: {percent.anchor_string().test(val)}")


def advanced_examples():
    """Advanced pattern building examples"""
    print("\n=== Advanced Examples ===")

    # Complex email validation with anchoring
    strict_email = S.email().anchor_string().ignore_case()
    print(f"Strict email: {strict_email}")

    # Password requirements: 8+ chars, 1 uppercase, 1 lowercase, 1 digit
    password = (
        S.any_char()
        .at_least(8)  # At least 8 characters
        .followed_by(
            S.any_char().zero_or_more() + S.uppercase() + S.any_char().zero_or_more()
        )  # Has uppercase
        .followed_by(
            S.any_char().zero_or_more() + S.lowercase() + S.any_char().zero_or_more()
        )  # Has lowercase
        .followed_by(
            S.any_char().zero_or_more() + S.digit() + S.any_char().zero_or_more()
        )  # Has digit
        .anchor_string()
    )

    print(f"Password pattern: {password}")

    # CSV-like pattern with quoted fields
    quoted_field = S.literal('"') + S.not_char('"').zero_or_more() + S.literal('"')
    unquoted_field = S.not_char('",\n').zero_or_more()
    csv_field = S.choice(quoted_field, unquoted_field)
    csv_row = csv_field + (S.literal(",") + csv_field).zero_or_more()

    print(f"CSV row: {csv_row}")


def comparison_old_vs_new():
    """Compare old API vs new unified API"""
    print("\n=== Old vs New API Comparison ===")

    print("OLD WAY (multiple imports, less discoverable):")
    print("""
    from scrive import digit, exactly, one_or_more, separated_by
    from scrive.patterns import email
    from scrive.anchors import start_of_string, end_of_string

    # IPv4 pattern - hard to read
    ipv4 = separated_by(digit().between(1, 3), exactly("."), 4)
    ipv4 = start_of_string() + ipv4 + end_of_string()

    # Email validation
    email_pattern = email().start_of_string().end_of_string()
    """)

    print("NEW WAY (single import, discoverable):")
    print("""
    from scrive import S

    # IPv4 pattern - clear and readable
    ipv4 = S.number_range(0, 255).separated_by(S.literal("."), 4).anchor_string()
    # Or use built-in
    ipv4 = S.ipv4().anchor_string()

    # Email validation
    email_pattern = S.email().anchor_string()
    """)

    # Show actual patterns
    old_style_ipv4 = (
        S.digit().between(1, 3)
        + S.literal(".")
        + S.digit().between(1, 3)
        + S.literal(".")
        + S.digit().between(1, 3)
        + S.literal(".")
        + S.digit().between(1, 3)
    )
    new_style_ipv4 = S.number_range(0, 255).separated_by(S.literal("."), 4)

    print(f"Old style result: {old_style_ipv4}")
    print(f"New style result: {new_style_ipv4}")


def fluent_chaining_demo():
    """Demonstrate the power of fluent method chaining"""
    print("\n=== Fluent Method Chaining ===")

    # Build complex pattern step by step
    username_pattern = (
        S.letter()  # Start with letter (1 char)
        .then(S.word().times(2, 19))  # Followed by 2-19 word chars (total: 3-20)
        .anchor_string()  # Exact match
    )

    print(f"Username pattern: {username_pattern}")

    # Test usernames
    usernames = ["abc", "user123", "a", "user_name_that_is_too_long_for_validation"]
    for username in usernames:
        valid = username_pattern.test(username)
        print(f"Username '{username}': {'✓' if valid else '✗'}")


def template_and_substitution():
    """Examples of pattern templates and substitution"""
    print("\n=== Templates and Substitution ===")

    # Create reusable pattern template
    bounded_word = S.placeholder("start") + S.word().one_or_more() + S.placeholder("end")

    # Substitute different boundaries
    html_tag = bounded_word.template(start="<", end=">")
    parenthesized = bounded_word.template(start="(", end=")")

    print(f"HTML tag pattern: {html_tag}")
    print(f"Parenthesized pattern: {parenthesized}")

    # Test them
    print(f"'<div>' matches HTML: {html_tag.test('<div>')}")
    print(f"'(word)' matches parenthesized: {parenthesized.test('(word)')}")


if __name__ == "__main__":
    """Run all examples"""
    basic_patterns()
    quantifier_examples()
    anchoring_examples()
    combination_examples()
    common_patterns()
    number_patterns()
    advanced_examples()
    comparison_old_vs_new()
    fluent_chaining_demo()
    template_and_substitution()

    print("\n=== Summary ===")
    print("The unified S factory API provides:")
    print("✓ Single import point")
    print("✓ Discoverable methods")
    print("✓ Consistent naming")
    print("✓ Fluent chaining")
    print("✓ Built-in common patterns")
    print("✓ Better IDE support")
