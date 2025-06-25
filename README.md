![Scrive Cover](https://github.com/user-attachments/assets/f6165bac-8a35-4f48-a665-2bb330199854)

# Scrive

**Scrive** (rooted from "Scribe") is a modern, fluent regex pattern builder for Python that makes complex regular expressions readable, maintainable, and discoverable.

## Why Scrive?

**Before** - Traditional regex is cryptic and hard to maintain:

```python
import re
pattern = re.compile(r'^[a-zA-Z]\w{2,19}$')  # What does this do?
```

**After** - Scrive makes it self-documenting:

```python
from scrive import S
pattern = S.letter().then(S.word().between(2, 19)).anchor_string()  # Clear!
```

## Installation

Install Scrive using `pip` or your favorite package manager.

```bash
pip install scrive
```

After that, simply import the `S` class:

```python
from scrive import S  # easy as that!
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
S.literal("hello")          # Exact text (escaped)
S.char("a", "e", "i")       # Character class [aei]
S.char_range("a", "z")      # Range [a-z]
S.raw(r"\d+")               # Raw regex (unescaped)

# Common character classes
S.digit()                   # \d (digits)
S.letter()                  # [a-zA-Z] (letters)
S.word()                    # \w (word characters)
S.whitespace()              # \s (whitespace)
S.ascii()                   # [ -~] (ascii characters)
S.any_char()                # . (any character)
# ...and more

# Negated classes
S.not_digit()               # \D
S.not_letter()              # \W (non-word characters)
S.not_word()                # \W (non-word characters)
S.not_whitespace()          # \S (non-whitespace characters)
S.not_ascii()               # [^ -~] (non-ascii characters)
S.not_char("aeiou")         # [^aeiou] (everything but the given characters)
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
pattern.followed_by(S.digit())          # (?=\d) positive lookahead
pattern.not_followed_by(S.digit())      # (?!\d) negative lookahead
pattern.preceded_by(S.letter())         # (?<=[a-zA-Z]) positive lookbehind
pattern.not_preceded_by(S.letter())     # (?<![a-zA-Z]) negative lookbehind
```

### Combinators

```python
# Sequence (concatenation)
S.literal("hello").then(S.space()).then(S.word().one_or_more())

# Alternation (OR)
S.choice("cat", "dog", "bird")              # Optimized to (?:cat|dog|bird)

# Repetition with separators
S.digit().separated_by(S.literal("."), 4)   # \d\.\d\.\d\.\d
```

### Joining Patterns

```python
# Sequence method
# (does not support alternation on its own)
S.sequence(S.literal("hello"), S.space(), S.word().one_or_more())

# Operators
S.literal("hello") + S.space() + S.word().one_or_more()
S.literal("cat") | S.literal("dog") | S.literal("bird")

# Chaining
S.literal("hello").then(S.space()).then(S.word().one_or_more())
S.literal("cat").or_else(S.literal("dog")).or_else(S.literal("bird"))
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
pattern.test("hello")                   # Boolean match (substring search)
pattern.exact_match("hello")            # Boolean exact match
pattern.match("hello")                  # Match from start
pattern.search("hello")                 # Search anywhere
pattern.find_all("hello world")         # Find all matches
pattern.split("a,b,c")                  # Split by pattern
pattern.replace("text", "replacement")  # Replace matches

# Compilation
compiled = pattern.compile()            # Get re.Pattern object
```

### Examples

```python
# API endpoint validation
api_endpoint = (
    S.literal("/api/v")
    .then(S.digit().one_or_more())
    .then(S.literal("/"))
    .then(S.word().one_or_more())
    .anchor_string()
)

# Database field validation
user_id = S.literal("user_").then(S.digit().times(6, 12)).anchor_string()

# Log file parsing
nginx_log = S.sequence(
    S.ipv4().group("client_ip"),
    S.space(),
    S.literal("[").then(S.none_of("]").one_or_more().group("timestamp")).then(S.literal("]")),
    S.space(),
    S.literal('"').then(S.any_char().one_or_more().group("request")).then(S.literal('"'))
)
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

# Credit card validation with multiple formats
credit_card = S.choice(
    # Visa: 4xxx-xxxx-xxxx-xxxx
    S.literal("4").then(S.digit().times(3)).then(S.literal("-")).then(
        S.digit().times(4).then(S.literal("-")).times(2)
    ).then(S.digit().times(4)),
    # MasterCard: 5xxx xxxx xxxx xxxx
    S.char("5").then(S.digit().times(3)).then(S.space()).then(
        S.digit().times(4).then(S.space()).times(2)
    ).then(S.digit().times(4))
).anchor_string()

# International phone numbers
phone = S.choice(
    # US format: (555) 123-4567
    S.literal("(").then(S.digit().times(3)).then(S.literal(") "))
     .then(S.digit().times(3)).then(S.literal("-")).then(S.digit().times(4)),
    # International: +1-555-123-4567
    S.literal("+").then(S.digit().times(1, 3)).then(S.literal("-"))
     .then(S.digit().times(3)).then(S.literal("-")).then(S.digit().times(3))
     .then(S.literal("-")).then(S.digit().times(4))
).anchor_string()
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

## Performance & Optimization

Scrive includes an intelligent optimization engine that automatically improves your patterns:

### Automatic Pattern Optimization

```python
# Character ranges - automatically detects sequences
S.char("a", "b", "c", "d", "e")     # Automatically becomes [a-e]
S.char("0", "1", "2", "3")          # Automatically becomes [0-3]

# Choice optimization - converts to character classes when possible
S.choice("1", "2", "3", "4")        # Automatically becomes [1-4]
S.choice("cat", "dog", "bird")      # Stays as (?:cat|dog|bird)

# Smart grouping - only groups when necessary
S.choice("cat", "dog").one_or_more() # Becomes (?:cat|dog)+
S.digit().one_or_more()             # Stays as \d+ (no unnecessary grouping)

# Number range optimization
S.number_range(0, 255)              # Generates optimal IPv4 octet pattern
S.number_range(1, 100)              # Optimized numeric range matching
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
template = S.placeholder("start") + S.word().one_or_more() + S.placeholder("end")
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

---

**Made with ❤️ for Python developers who want readable regex patterns**

_"From fragmented complexity to unified elegance - Scrive makes regex patterns a joy to write and maintain."_

🧪 [Testing](tests/test_unified_api.py) | 🚀 [Examples](examples/examples_unified.py) | 📈 [Demo](examples/demo_unified_api.py)
