import re

from .core import Scrive
from .macros import choice, decimal_range, separated_by


# Helper functions to replace removed imports
def exactly(text: str) -> Scrive:
    return Scrive(re.escape(text))


def char(chars: str) -> Scrive:
    if len(chars) == 1:
        return Scrive(re.escape(chars))
    return Scrive(f"[{re.escape(chars)}]")


def digit() -> Scrive:
    return Scrive("\\d")


def letter() -> Scrive:
    return Scrive("[a-zA-Z]")


def word_char() -> Scrive:
    return Scrive("\\w")


def hexadecimal() -> Scrive:
    return Scrive("[0-9a-fA-F]")


def ascii() -> Scrive:
    return Scrive("[ -~]")


def maybe(pattern: Scrive) -> Scrive:
    return pattern.maybe()


def one_or_more(pattern: Scrive) -> Scrive:
    return pattern.one_or_more()


def zero_or_more(pattern: Scrive) -> Scrive:
    return pattern.zero_or_more()


def email() -> Scrive:
    """Match email address pattern."""
    username = one_or_more(word_char() | char("-._"))
    mail_server = one_or_more(word_char() | char("-."))
    domain = (word_char() | char("-.")).between(2, 6)
    return username + exactly("@") + mail_server + exactly(".") + domain


def url() -> Scrive:
    """Match robust URL pattern supporting various protocols and URL components."""
    protocol = choice("http", "https", "ftp", "ftps", "file", "ws", "wss") + exactly(
        "://"
    )

    # Optional credentials (user:pass@)
    credentials = maybe(
        one_or_more(word_char() | char("-._"))
        + maybe(exactly(":") + one_or_more(word_char() | char("-._")))
        + exactly("@")
    )

    # Domain: can include subdomains, IDN characters, IP addresses
    # Support for IPv4 addresses in brackets or regular domain names
    ipv4_pattern = (
        digit().between(1, 3)
        + exactly(".")
        + digit().between(1, 3)
        + exactly(".")
        + digit().between(1, 3)
        + exactly(".")
        + digit().between(1, 3)
    )

    domain_name = one_or_more(word_char() | char("-.")) + maybe(
        exactly(".") + letter().between(2, 6)
    )

    domain = choice(
        exactly("[") + ipv4_pattern + exactly("]"),  # IPv4 in brackets
        ipv4_pattern,  # Plain IPv4
        domain_name,  # Regular domain
    )

    # Optional port
    port = maybe(exactly(":") + digit().between(1, 5))

    # Path: can include various URL-safe characters
    path_segment = zero_or_more(ascii())
    path = maybe(
        exactly("/") + maybe(path_segment + zero_or_more(exactly("/") + path_segment))
    )

    # Query parameters
    query = maybe(exactly("?") + zero_or_more(ascii()))

    # Fragment
    fragment = maybe(exactly("#") + zero_or_more(ascii()))

    return protocol + credentials + domain + port + path + query + fragment


def ipv4() -> Scrive:
    """Match IPv4 address pattern."""
    return separated_by(decimal_range(0, 255), exactly("."), 4)


def ipv6() -> Scrive:
    """Match IPv6 address pattern."""
    hex = hexadecimal().times(4)
    return separated_by(hex, exactly(":"), 8)


def phone_number() -> Scrive:
    """Match robust phone number pattern supporting various international formats."""
    # Country code: 1-4 digits, optionally preceded by +
    country_code = maybe(exactly("+") + digit().between(1, 4) + maybe(char(" -()")))

    # Area code: 2-4 digits, often in parentheses or separated by space/dash
    area_code = choice(
        exactly("(") + digit().between(2, 4) + exactly(")"),  # (123)
        digit().between(2, 4),  # 123
    ) + maybe(char(" -"))

    # Main number: typically 6-10 digits with optional separators
    # Split into groups to handle common patterns like 123-4567 or 123 4567
    main_number = (
        digit().between(3, 4)
        + maybe(char(" -."))
        + digit().between(3, 4)
        + maybe(char(" -.") + digit().between(0, 4))  # Optional extension digits
    )

    # Extension: optional extension number
    extension = maybe(
        maybe(char(" "))
        + choice("ext", "extension", "x", "X")
        + maybe(char(" ."))
        + digit().between(1, 6)
    )

    return country_code + maybe(area_code) + main_number + extension


def credit_card() -> Scrive:
    """Match credit card number pattern."""
    return (
        digit().times(4)
        + maybe(char(" -"))
        + digit().times(4)
        + maybe(char(" -"))
        + digit().times(4)
        + maybe(char(" -"))
        + digit().times(4)
    )


_HEX = hexadecimal()


def uuidv1() -> Scrive:
    """Match UUID v1 pattern."""
    return (
        _HEX.times(8)
        + exactly("-")
        + _HEX.times(4)
        + exactly("-")
        + exactly("1")
        + _HEX.times(3)
        + exactly("-")
        + char("89abAB")
        + _HEX.times(3)
        + exactly("-")
        + _HEX.times(12)
    )


def uuidv2() -> Scrive:
    """Match UUID v2 pattern."""
    return (
        _HEX.times(8)
        + exactly("-")
        + _HEX.times(4)
        + exactly("-")
        + exactly("2")
        + _HEX.times(3)
        + exactly("-")
        + char("89abAB")
        + _HEX.times(3)
        + exactly("-")
        + _HEX.times(12)
    )


def uuidv3() -> Scrive:
    """Match UUID v3 pattern."""
    return (
        _HEX.times(8)
        + exactly("-")
        + _HEX.times(4)
        + exactly("-")
        + exactly("3")
        + _HEX.times(3)
        + exactly("-")
        + char("89abAB")
        + _HEX.times(3)
        + exactly("-")
        + _HEX.times(12)
    )


def uuidv4() -> Scrive:
    """Match UUID v4 pattern."""
    return (
        _HEX.times(8)
        + exactly("-")
        + _HEX.times(4)
        + exactly("-")
        + exactly("4")
        + _HEX.times(3)
        + exactly("-")
        + char("89abAB")
        + _HEX.times(3)
        + exactly("-")
        + _HEX.times(12)
    )


def uuidv5() -> Scrive:
    """Match UUID v5 pattern."""
    return (
        _HEX.times(8)
        + exactly("-")
        + _HEX.times(4)
        + exactly("-")
        + exactly("5")
        + _HEX.times(3)
        + exactly("-")
        + char("89abAB")
        + _HEX.times(3)
        + exactly("-")
        + _HEX.times(12)
    )


def uuidv6() -> Scrive:
    """Match UUID v6 pattern."""
    return (
        _HEX.times(8)
        + exactly("-")
        + _HEX.times(4)
        + exactly("-")
        + exactly("6")
        + _HEX.times(3)
        + exactly("-")
        + char("89abAB")
        + _HEX.times(3)
        + exactly("-")
        + _HEX.times(12)
    )


def uuidv7() -> Scrive:
    """Match UUID v7 pattern."""
    return (
        _HEX.times(8)
        + exactly("-")
        + _HEX.times(4)
        + exactly("-")
        + exactly("7")
        + _HEX.times(3)
        + exactly("-")
        + char("89abAB")
        + _HEX.times(3)
        + exactly("-")
        + _HEX.times(12)
    )


def uuidv8() -> Scrive:
    """Match UUID v8 pattern."""
    return (
        _HEX.times(8)
        + exactly("-")
        + _HEX.times(4)
        + exactly("-")
        + exactly("8")
        + _HEX.times(3)
        + exactly("-")
        + char("89abAB")
        + _HEX.times(3)
        + exactly("-")
        + _HEX.times(12)
    )
