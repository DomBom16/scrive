![Scrive Cover](https://github.com/user-attachments/assets/f6165bac-8a35-4f48-a665-2bb330199854)

# Scrive

[![Version](https://img.shields.io/badge/version-2.0.0-blue?style=for-the-badge)](https://github.com/your-repo/scrive)
[![Python](https://img.shields.io/badge/python-3.7+-green?style=for-the-badge)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

**Scrive** (rooted from "Scribe") is a modern, fluent regex pattern builder for Python that makes complex regular expressions readable, maintainable, and discoverable.

## Why Scrive?

**Before** - Traditional regex is cryptic and hard to maintain:

```python
import re
pattern = re.compile(r'^[a-zA-Z][\w]{2,19}$')  # What does this do?
```

**After** - Scrive makes it self-documenting:

```python
from scrive import S
pattern = S.letter().then(S.word().times(2, 19)).anchor_string()  # Clear!
```

## Key Features

- **🎯 Single Import** - Everything through `from scrive import S`
- **🔗 Fluent Chaining** - Build patterns step by step with method chaining
- **📚 Built-in Patterns** - Email, URL, IPv4, phone numbers, and more
- **🚀 Auto-Optimization** - Patterns are automatically optimized for performance
- **💡 IDE-Friendly** - Excellent autocomplete and discoverability
- **🔄 Backward Compatible** - Existing code continues to work
- **✅ Well-Tested** - Comprehensive test suite with 82+ tests

## Installation

```bash
pip install scrive
```

## Quick Start

```python
from scrive import S

# Email validation
email = S.email().anchor_string()
print(email.test("user@example.com"))  # True

# IPv4 address matching
ipv4 = S.number_range(0, 255).separated_by(S.literal("."), 4).anchor_string()
print(ipv4.test("192.168.1.1"))  # True

# Username validation (3-20 chars, starts with letter)
username = S.letter().then(S.word().times(2, 19)).anchor_string()
print(username.test("user123"))  # True

# Phone number with multiple formats
phone = S.choice(
    S.literal("(").then(S.digit().times(3)).then(S.literal(") "))
     .then(S.digit().times(3)).then(S.literal("-")).then(S.digit().times(4)),
    S.digit().times(3).then(S.literal("-"))
     .then(S.digit().times(3)).then(S.literal("-")).then(S.digit().times(4))
).anchor_string()
```

## Core API

### Pattern Creation

```python
# Text and characters
S.literal("hello")           # Exact text (escaped)
S.char("a", "e", "i")       # Character class [aei]
S.char_range("a", "z")      # Range [a-z]
S.raw(r"\d+")               # Raw regex (unescaped)

# Common character classes
S.digit()                   # \d (digits)
S.letter()                  # [a-zA-Z] (letters)
S.word()                    # \w (word characters)
S.whitespace()              # \s (whitespace)
S.any_char()                # . (any character)

# Negated classes
S.non_digit()               # \D
S.none_of("aeiou")          # [^aeiou] (consonants)
```

### Quantifiers

```python
# Basic quantifiers
pattern.maybe()             # ? (0 or 1)
pattern.one_or_more()       # + (1 or more)
pattern.zero_or_more()      # * (0 or more)

# Exact counts
pattern.times(3)            # {3} (exactly 3)
pattern.times(2, 5)         # {2,5} (between 2 and 5)
pattern.at_least(2)         # {2,} (2 or more)
pattern.at_most(5)          # {,5} (up to 5)

# Lazy versions
pattern.maybe_lazy()        # ??
pattern.one_or_more_lazy()  # +?
```

### Anchors & Boundaries

```python
# String anchors
pattern.anchor_string()     # ^pattern$ (exact match)
pattern.start_of_string()   # ^ (start)
pattern.end_of_string()     # $ (end)

# Word boundaries
pattern.word_boundary()     # \b around pattern
S.word_boundary()           # \b standalone
S.non_word_boundary()       # \B standalone
```

### Lookaround Assertions

```python
# Lookahead/lookbehind
pattern.followed_by(S.digit())      # (?=\d) positive lookahead
pattern.not_followed_by(S.digit())  # (?!\d) negative lookahead
pattern.preceded_by(S.letter())     # (?<=[a-zA-Z]) positive lookbehind
pattern.not_preceded_by(S.letter()) # (?<![a-zA-Z]) negative lookbehind
```

### Combinators

```python
# Sequence (concatenation)
S.literal("hello").then(S.space()).then(S.word().one_or_more())

# Alternation (OR)
S.choice("cat", "dog", "bird")      # Optimized to (?:cat|dog|bird)

# Repetition with separators
S.digit().separated_by(S.literal("."), 4)  # For IPv4: \d\.\d\.\d\.\d
```

## Built-in Patterns

```python
# Common patterns
S.email()                   # Email addresses
S.url()                     # URLs
S.ipv4()                    # IPv4 addresses
S.ipv6()                    # IPv6 addresses
S.phone()                   # Phone numbers
S.credit_card()             # Credit card numbers

# UUID patterns
S.uuid()                    # Any UUID version
S.uuid(4)                   # Specific version (1-8)

# Number patterns
S.integer()                 # Integers with optional sign
S.decimal()                 # Decimal numbers
S.number_range(1, 100)      # Numbers in specific range
```

## Testing & Compilation

```python
# Pattern testing
pattern.test("hello")               # Boolean match (substring search)
pattern.exact_match("hello")       # Boolean exact match
pattern.match("hello")              # Match from start
pattern.search("hello")             # Search anywhere
pattern.find_all("hello world")    # Find all matches
pattern.split("a,b,c")             # Split by pattern
pattern.replace("text", "replacement")  # Replace matches

# Compilation
compiled = pattern.compile()        # Get re.Pattern object
```

## Real-World Examples

### Form Validation

```python
# Password: 8+ chars, uppercase, lowercase, digit
password = (
    S.start_of_string()
    .then(S.raw("(?=.*[A-Z])"))      # Has uppercase
    .then(S.raw("(?=.*[a-z])"))      # Has lowercase
    .then(S.raw("(?=.*\\d)"))        # Has digit
    .then(S.any_char().at_least(8))  # At least 8 chars
    .then(S.end_of_string())
)

# Credit card (basic format)
credit_card = S.digit().times(4).then(
    S.char(" -").maybe().then(S.digit().times(4))
).times(3).anchor_string()
```

### Data Extraction

```python
# Extract version numbers
version = S.sequence(
    S.digit().one_or_more().group("major"),
    S.literal("."),
    S.digit().one_or_more().group("minor"),
    S.literal(".").then(S.digit().one_or_more().group("patch")).maybe()
)

# Extract hashtags
hashtag = S.literal("#").then(S.word().one_or_more().group("tag"))

# Log parsing (Apache format)
apache_log = S.sequence(
    S.ipv4().group("ip"),
    S.space(),
    S.literal("-").space(),
    S.literal("-").space(),
    S.literal("[").then(S.none_of("]").one_or_more().group("timestamp")).then(S.literal("]")),
    S.space(),
    S.literal('"').then(S.none_of('"').one_or_more().group("request")).then(S.literal('"')),
    S.space(),
    S.digit().one_or_more().group("status"),
    S.space(),
    S.digit().one_or_more().group("size")
)
```

### Complex Patterns

```python
# CSV parser with quoted fields
quoted_field = S.literal('"').then(S.none_of('"').zero_or_more()).then(S.literal('"'))
unquoted_field = S.none_of('",\n').one_or_more()
csv_field = S.choice(quoted_field, unquoted_field)
csv_row = csv_field.then(S.literal(",").then(csv_field).zero_or_more())

# URL with specific domains
enterprise_email = (
    S.word().one_or_more()
    .then(S.literal("@"))
    .then(S.choice("company", "enterprise"))
    .then(S.literal("."))
    .then(S.choice("com", "org", "net"))
    .anchor_string()
    .ignore_case()
)
```

## Migration from 1.x

The 2.0 unified API is designed for easy migration:

### Before (1.x - Fragmented)

```python
from scrive import digit, exactly, one_or_more, separated_by
from scrive.patterns import email
from scrive.anchors import start_of_string, end_of_string

# Multiple imports, hard to discover
ipv4 = separated_by(digit().between(1, 3), exactly("."), 4)
ipv4 = start_of_string() + ipv4 + end_of_string()
```

### After (2.0 - Unified)

```python
from scrive import S

# Single import, everything discoverable
ipv4 = S.number_range(0, 255).separated_by(S.literal("."), 4).anchor_string()
# Or use built-in:
ipv4 = S.ipv4().anchor_string()
```

### Migration Steps

1. **Replace imports**: Change to `from scrive import S`
2. **Use factory methods**: Replace function calls with `S.method()`
3. **Leverage built-ins**: Use `S.email()`, `S.ipv4()` instead of building from scratch
4. **Update method names**: `before()` → `followed_by()`, etc.

## Performance

Scrive automatically optimizes patterns:

```python
# Character ranges
S.char("a", "b", "c", "d", "e")     # Becomes [a-e]

# Choice optimization
S.choice("1", "2", "3", "4")        # Becomes [1-4]

# Smart grouping
S.choice("cat", "dog").one_or_more() # Becomes (?:cat|dog)+
S.digit().one_or_more()             # Stays as \d+ (no unnecessary grouping)
```

## Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Add new patterns**: Use the `S` factory structure
2. **Improve optimization**: Enhance pattern optimization algorithms
3. **Add tests**: Maintain our comprehensive test coverage
4. **Update docs**: Keep examples using the unified API

### Development Setup

```bash
git clone https://github.com/your-repo/scrive.git
cd scrive
pip install -e .
python -m pytest test_unified_api.py -v
```

## Advanced Features

### Pattern Templates

```python
# Create reusable templates
template = S.raw("{start}\\w+{end}")
html_tag = template.template(start="<", end=">")
parens = template.template(start="\\(", end="\\)")
```

### Flags and Modifiers

```python
# Global flags
pattern.ignore_case()       # Case insensitive
pattern.multiline()         # Multiline mode
pattern.dotall()           # . matches newlines

# Inline flags
pattern.case_insensitive_group()  # (?i:pattern)
```

### Custom Patterns

```python
# Build your own library of patterns
def ssn():
    return S.digit().times(3).then(S.literal("-")).then(
        S.digit().times(2)).then(S.literal("-")).then(S.digit().times(4))

def mac_address():
    hex_pair = S.hexadecimal().times(2)
    return hex_pair.separated_by(S.literal(":"), 6)
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

### v2.0.0 - Unified API

- ✨ **New**: Unified `S` factory class
- ✨ **New**: Enhanced method chaining with intuitive aliases
- ✨ **New**: Built-in common patterns (`S.email()`, `S.ipv4()`, etc.)
- ✨ **New**: Automatic pattern optimization
- ✨ **New**: Comprehensive test suite (82+ tests)
- 🔄 **Breaking**: Simplified module structure
- ♻️ **Removed**: Legacy scattered modules
- 🚀 **Improved**: Developer experience and discoverability

### v1.x - Legacy API

- Basic pattern building functionality
- Separate modules for different features

---

**Made with ❤️ for Python developers who want readable regex patterns**

🧪 [Testing](test_unified_api.md) | 🚀 [Examples](examples_unified.py) | 📈 [Demo](demo_unified_api.py)
