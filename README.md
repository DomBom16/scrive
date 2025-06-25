# Scrive - Pythonic Regex Pattern Builder

A Pythonic regex pattern builder library that provides a fluent, chainable API for building regular expressions with named capture groups, operator overloading, and intuitive method chaining.

## Features

- 🔗 **Fluent API**: Chain methods to build complex regex patterns intuitively
- 🏷️ **Named Capture Groups**: Easy-to-use named groups with `grouped_as()`
- 🔍 **Lookahead/Lookbehind**: Simple assertion methods like `after()` and `before()`
- 📝 **Backreferences**: Reference previously captured groups with `reference_to()` and `ref()`
- 🎯 **Common Patterns**: Built-in patterns for email, URL, IPv4, phone numbers, etc.
- 🐍 **Pythonic**: Operator overloading (`+`, `|`) and snake_case methods
- 🚀 **Performance**: Compiles to native Python regex objects
- 📖 **Readable**: Write regex patterns that are self-documenting
- 🧩 **Raw Regex Support**: Inject raw regex with `raw()` for complex patterns
- 🔄 **Pattern Negation**: Invert patterns with `invert()` and `negated()`
- 🔗 **Chained Transformations**: Chain text replacements and transformations
- 💬 **Inline Comments**: Add comments to patterns with `comment()` in verbose mode
- 🌍 **Unicode Support**: Full Unicode property matching and script support
- ✅ **Custom Validators**: Add business logic validation with `where()`
- 📋 **Pattern Templating**: Template patterns with variable substitution
- 🔍 **Introspection**: Debug patterns with `steps()` and `describe()`
- 🎭 **Case Control**: Fine-grained case sensitivity with group-level control

## Installation

```bash
# Copy scrive.py to your project directory
# No external dependencies required (uses only Python standard library)
```

## Quick Start

```python
from scrive import exactly, digit, one_or_more, create_regexp

# Create a pattern for ID matching
ID_RE = exactly("id-") + digit().times(5).grouped_as("id")

# Test the pattern
text = "some id-23490 here we go"
match = ID_RE.search(text)
if match:
    print(f"ID: {match.groupdict()['id']}")  # Output: ID: 23490
```

## Core Concepts

### Basic Pattern Building

```python
from scrive import exactly, digit, word_char, one_or_more

# Simple exact match
pattern = exactly("hello")

# Character classes
digits = digit()
words = word_char()

# Quantifiers
one_or_more_digits = one_or_more(digit())
optional_s = maybe("s")
```

### Method Chaining

```python
# Build complex patterns by chaining methods
email_pattern = (
    one_or_more(word_char())
    .and_("@")
    .and_(one_or_more(word_char()))
    .and_(".")
    .and_(one_or_more(word_char()))
)
```

### Pythonic Operators

```python
# Use + for concatenation
greeting = exactly("hello") + exactly(" ") + exactly("world")

# Use | for alternation
choice = exactly("cat") | exactly("dog")
```

### Named Capture Groups

```python
# Create named groups for easy extraction
semver_pattern = create_regexp(
    one_or_more(digit()).grouped_as("major"),
    exactly("."),
    one_or_more(digit()).grouped_as("minor"),
    maybe(exactly("."), one_or_more(digit()).grouped_as("patch"))
)

match = semver_pattern.search("version 1.2.3")
if match:
    groups = match.groupdict()
    print(f"Major: {groups['major']}, Minor: {groups['minor']}")
```

## API Reference

### Core Classes

#### `ScribePattern`

The main class for building regex patterns.

**Operators:**

- `+` - Concatenate patterns (equivalent to `and_()`)
- `|` - Create alternation (equivalent to `or_()`)

**Methods:**

- `and_(*others)` - Concatenate patterns
- `or_(*others)` - Create alternation (OR)
- `times(count)` - Apply quantifier {n} or {n,m}
- `one_or_more()` - Apply + quantifier
- `zero_or_more()` - Apply \* quantifier
- `maybe()` - Apply ? quantifier
- `grouped_as(name)` - Create named capture group
- `reference_to(name)` - Create backreference to named group

**Assertions:**

- `after(pattern)` - Positive lookbehind
- `before(pattern)` - Positive lookahead
- `not_after(pattern)` - Negative lookbehind
- `not_before(pattern)` - Negative lookahead

**Anchors:**

- `start_of_string()` - Add ^ anchor
- `end_of_string()` - Add $ anchor
- `word_boundary()` - Add \b boundary
- `start_of_line()` - Add ^ with multiline flag
- `end_of_line()` - Add $ with multiline flag

**Flags:**

- `ignore_case()` - Case insensitive matching
- `multiline()` - Multiline mode
- `dot_all()` - Dot matches newlines
- `verbose()` - Verbose mode for readable regex

**Enhanced Features:**

- `raw(regex)` - Inject raw regex without escaping
- `invert()` / `negated()` - Negate/invert the pattern
- `ref(number)` - Create numbered backreference
- `unicode(category)` - Add Unicode property pattern
- `where(validator)` - Add custom validation function
- `comment(text)` - Add inline comment (verbose mode)
- `case_insensitive_group()` - Wrap in case-insensitive group
- `case_sensitive_group()` - Wrap in case-sensitive group
- `template(**kwargs)` - Template with variable substitution
- `describe()` - Get human-readable pattern description
- `steps()` - Get list of build steps for debugging
- `debug()` - Get comprehensive debug information
- `copy()` - Create independent copy of pattern

**Text Transformations:**

- `replace(old, new)` - Chain string replacement
- `remove(pattern)` - Chain pattern removal
- `regex_sub(pattern, repl)` - Chain regex substitution
- `chain_sub(repl)` - Add substitution to chain
- `apply_transformations(text)` - Apply all chained transformations

**Testing & Matching:**

- `test(text)` - Test if pattern matches
- `test_with_validator(text)` - Test with custom validator
- `search(text)` - Find first match
- `find_all(text)` - Find all matches
- `compile()` - Compile to Python regex object

### Factory Functions

#### Character Classes

- `char(chars=None)` - Any character or specific chars
- `digit()` - Digit character (\d)
- `word_char()` - Word character (\w)
- `whitespace()` - Whitespace character (\s)
- `letter()` - Any letter [a-zA-Z]
- `uppercase()` - Uppercase letter [A-Z]
- `lowercase()` - Lowercase letter [a-z]

#### Quantifiers

- `one_or_more(*patterns)` - One or more (+)
- `zero_or_more(*patterns)` - Zero or more (\*)
- `maybe(*patterns)` - Optional (?)

### Utilities

- `exactly(text)` - Exact text match (escaped)
- `one_of(*chars)` - Character class [abc]
- `none_of(*chars)` - Negated character class [^abc]
- `char_range(start, end)` - Character range [a-z]
- `choice(*patterns)` - Alternation (a|b|c)
- `separated_by(element, separator, count)` - Repeat element with separator
- `decimal_range(min, max)` - Match numbers in range

### Unicode Support

- `unicode_category(category)` - Unicode general category (L, Lu, Nd, etc.)
- `unicode_script(script)` - Unicode script (Latin, Cyrillic, etc.)
- `unicode_block(block)` - Unicode block (BasicLatin, etc.)
- `not_unicode_category(category)` - Negated Unicode category
- `not_unicode_script(script)` - Negated Unicode script
- `not_unicode_block(block)` - Negated Unicode block

**Convenience Unicode Functions:**

- `unicode_letter()`, `unicode_digit()`, `unicode_uppercase()`, etc.
- `unicode_latin()`, `unicode_cyrillic()`, `unicode_arabic()`, etc.
- `unicode_emoji()` - Common emoji patterns

### Common Patterns

Pre-built patterns for common use cases:

```python
from scrive import email, url, ipv4, phone_number, uuid

# Email validation
email_regex = email().compile()
print(email_regex.search("test@example.com") is not None)

# URL matching
url_regex = url().compile()
print(url_regex.search("https://example.com/path") is not None)

# IPv4 address
ip_regex = ipv4().compile()
print(ip_regex.search("192.168.1.1") is not None)
```

## Enhanced Features Examples

### Raw Regex Integration

```python
from scrive import exactly, digit, any_char

# Mix Scrive patterns with raw regex for complex cases
log_pattern = (
    exactly("[")
    .raw(r"\d{4}-\d{2}-\d{2}")  # ISO date format
    .exactly(" ")
    .raw(r"\d{2}:\d{2}:\d{2}")  # Time format
    .exactly("] ")
    .and_(any_char().one_or_more())
)

# Complex password validation with raw lookaheads
password_strength = (
    any_char()
    .raw(r"(?=.*[a-z])")      # Must contain lowercase
    .raw(r"(?=.*[A-Z])")      # Must contain uppercase
    .raw(r"(?=.*\d)")         # Must contain digit
    .raw(r"(?=.*[@$!%*?&])")  # Must contain special char
    .between(8, 128)
)
```

### Pattern Negation

```python
from scrive import char, email

# Character class inversion
vowels = char("aeiouAEIOU")
consonants = vowels.invert()  # [^aeiouAEIOU]

# Complex pattern negation
email_pattern = email()
non_email = email_pattern.negated()  # Matches non-email text
```

### Chained Text Transformations

```python
from scrive import Scrive

# HTML entity cleanup chain
cleanup = (
    Scrive("")
    .replace("&amp;", "&")
    .replace("&lt;", "<")
    .replace("&gt;", ">")
    .remove("SPAM")
    .regex_sub(r"(\d{3})(\d{3})(\d{4})", r"(\1) \2-\3")  # Format phones
)

dirty_text = "&lt;p&gt;Call 5551234567 SPAM"
clean_text = cleanup.apply_transformations(dirty_text)
# Result: "<p>Call (555) 123-4567 "
```

### Custom Validators

```python
from scrive import digit

# Age validation with business logic
def age_validator(match):
    age = int(match.group())
    return 13 <= age <= 120

age_pattern = digit().between(1, 3).where(age_validator)

print(age_pattern.test_with_validator("25"))   # True
print(age_pattern.test_with_validator("150"))  # False

# Credit card with Luhn algorithm validation
def luhn_validator(match):
    number = match.group().replace(" ", "").replace("-", "")
    # Implement Luhn algorithm
    return luhn_check(number)

cc_pattern = (
    digit().times(4).and_(char(" -").maybe())
    .and_(digit().times(4)).and_(char(" -").maybe())
    .and_(digit().times(4)).and_(char(" -").maybe())
    .and_(digit().times(4))
    .where(luhn_validator)
)
```

### Pattern Templating

```python
from scrive import Scrive, word_char, digit, any_char

# SQL query template
sql_template = Scrive("SELECT {fields} FROM {table} WHERE {condition}")

sql_pattern = sql_template.template(
    fields=word_char().one_or_more().separated_by(exactly(", "), 3),
    table=word_char().one_or_more(),
    condition=word_char().one_or_more().and_(exactly(" = ")).and_(any_char().one_or_more())
)

# Configuration file template
config_template = Scrive("{section}.{key} = {value}")
config_pattern = config_template.template(
    section=word_char().one_or_more(),
    key=word_char().one_or_more(),
    value=any_char().one_or_more()
)
```

### Unicode Support

```python
from scrive import unicode_category, unicode_script, unicode_latin

# Match any Unicode letter
letters = unicode_category("L")

# Match specific scripts
chinese = unicode_script("Han")
arabic = unicode_script("Arabic")

# Match emoji (basic approach)
emoji = unicode_block("Emoticons")

# Combine with regular patterns
username = unicode_latin().one_or_more().and_(digit().zero_or_more())
```

### Inline Comments and Debugging

```python
from scrive import digit, exactly, char

# Complex pattern with comments
credit_card = (
    digit().times(4).comment("First group")
    .and_(char(" -").maybe()).comment("Optional separator")
    .and_(digit().times(4)).comment("Second group")
    .and_(char(" -").maybe()).comment("Optional separator")
    .and_(digit().times(4)).comment("Third group")
    .and_(char(" -").maybe()).comment("Optional separator")
    .and_(digit().times(4)).comment("Fourth group")
    .verbose()  # Enable comments
)

# Debug pattern building
pattern = digit().one_or_more().grouped_as("number").ignore_case()
print("Steps:", pattern.steps())
print("Debug:", pattern.debug())
print("Description:", pattern.describe())
```

### Numbered Backreferences

```python
from scrive import word_char, exactly

# Palindrome detector
palindrome = (
    word_char().group()          # Group 1
    .and_(word_char().group())   # Group 2
    .ref(2)                      # Reference group 2
    .ref(1)                      # Reference group 1
)

print(palindrome.exact_match("abba"))  # True
print(palindrome.exact_match("test"))  # False

# HTML tag matching
html_tag = (
    exactly("<")
    .and_(word_char().one_or_more().group())  # Tag name in group 1
    .and_(exactly(">"))
    .and_(any_char().zero_or_more())          # Content
    .and_(exactly("</"))
    .ref(1)                                   # Same tag name
    .and_(exactly(">"))
)
```

## Advanced Examples

### Complex ID Validation

```python
from scrive import exactly, digit, letter, create_regexp

# Match IDs like "USER-123-ABC"
USER_ID = create_regexp(
    exactly("USER-"),
    digit().times(3).grouped_as("number"),
    exactly("-"),
    letter().times(3).grouped_as("code")
)

text = "Found USER-123-ABC in the system"
match = USER_ID.search(text)
if match:
    groups = match.groupdict()
    print(f"Number: {groups['number']}, Code: {groups['code']}")
```

### Log Parser

```python
from scrive import exactly, digit, one_or_more, whitespace, one_of

LOG_PATTERN = create_regexp(
    exactly("["),
    one_or_more(digit()).grouped_as("timestamp"),
    exactly("]"),
    whitespace(),
    one_of("INFO", "WARN", "ERROR").grouped_as("level"),
    whitespace(),
    one_or_more(char()).grouped_as("message")
)

log_line = "[1634567890] ERROR Database connection failed"
match = LOG_PATTERN.search(log_line)
if match:
    groups = match.groupdict()
    print(f"Level: {groups['level']}, Message: {groups['message']}")
```

### Password Validation

```python
from scrive import one_or_more, char, digit, uppercase

# Password must contain digits, uppercase, and be 8+ chars
password_pattern = (
    one_or_more(char())
    .before(one_or_more(char()).and_(digit()))  # Contains digit
    .before(one_or_more(char()).and_(uppercase()))  # Contains uppercase
    .at_least(8)  # At least 8 characters
)
```

### Palindrome Detection with Backreferences

```python
from scrive import word_char, one_or_more, char, create_regexp, ScribePattern

# Simple palindrome pattern (like "radar", "level")
PALINDROME = create_regexp(
    word_char().grouped_as("first"),
    word_char().grouped_as("second"),
    zero_or_more(char()),
    ScribePattern().reference_to("second"),
    ScribePattern().reference_to("first")
)
```

### Using Pythonic Operators

```python
from scrive import exactly, digit, word_char, one_or_more

# Traditional method chaining
traditional = exactly("hello").and_(" ").and_(exactly("world"))

# Pythonic operator usage
pythonic = exactly("hello") + exactly(" ") + exactly("world")

# Both produce the same result
assert traditional.pattern == pythonic.pattern

# Alternation with |
greeting = exactly("hello") | exactly("hi") | exactly("hey")
print(greeting.test("hello"))  # True
print(greeting.test("hi"))     # True
print(greeting.test("bye"))    # False
```

## Pythonic Features

### Snake Case Methods

All methods follow Python's snake_case convention:

```python
# Character classes
word_char()         # instead of wordChar()
non_digit()         # instead of nonDigit()
alpha_numeric()     # instead of alphaNumeric()

# Quantifiers
one_or_more()       # instead of oneOrMore()
zero_or_more()      # instead of zeroOrMore()

# Grouping
grouped_as("name")  # instead of groupedAs("name")
reference_to("name") # instead of referenceTo("name")

# Assertions
not_after()         # instead of notAfter()
not_before()        # instead of notBefore()

# Anchors
start_of_string()   # instead of startOfString()
end_of_string()     # instead of endOfString()
word_boundary()     # instead of wordBoundary()

# Flags
ignore_case()       # instead of ignoreCase()
dot_all()           # instead of dotAll()
```

### Operator Overloading

```python
from scrive import exactly, digit, word_char

# Concatenation with +
email_local = one_or_more(word_char()) + exactly("@")
email_domain = one_or_more(word_char()) + exactly(".") + word_char().times((2, 4))
email_pattern = email_local + email_domain

# Alternation with |
file_extension = exactly(".txt") | exactly(".pdf") | exactly(".doc")
```

## Testing

Run the test suite:

```bash
python test_scrive.py
```

The tests cover:

- Basic pattern creation and compilation
- Method chaining and combinations
- Operator overloading (`+` and `|`)
- Quantifiers and grouping
- Assertions and anchors
- Named capture groups and backreferences
- Common pattern validation
- Pythonic features and snake_case methods
- Edge cases and error handling

## Performance

The library compiles to native Python `re` module patterns, so performance is equivalent to hand-written regex patterns. The fluent API adds minimal overhead during pattern construction.

## Migration from magic-regexp

If you're migrating from the original magic-regexp library:

1. Change import: `from magic_regexp import ...` → `from scrive import ...`
2. Update class names: `RegexPattern` → `ScribePattern`
3. Convert methods to snake_case: `oneOrMore()` → `one_or_more()`
4. Update function names: `createRegExp()` → `create_regexp()`

## API Reference Summary

### New Enhancement Methods

| Method                 | Description            | Example                                        |
| ---------------------- | ---------------------- | ---------------------------------------------- |
| `raw(regex)`           | Inject raw regex       | `exactly("hello").raw(r"\d+")`                 |
| `invert()`             | Negate pattern         | `char("aeiou").invert()`                       |
| `ref(n)`               | Numbered backreference | `word_char().group().ref(1)`                   |
| `where(func)`          | Custom validator       | `digit().where(lambda m: int(m.group()) > 0)`  |
| `comment(text)`        | Add comment            | `digit().comment("age").verbose()`             |
| `template(**kw)`       | Variable substitution  | `Scrive("Hello {name}").template(name="John")` |
| `describe()`           | Human description      | `pattern.describe()`                           |
| `steps()`              | Build steps            | `pattern.steps()`                              |
| `replace(old, new)`    | Chain replacement      | `Scrive("").replace("old", "new")`             |
| `regex_sub(pat, repl)` | Chain regex sub        | `Scrive("").regex_sub(r"\d+", "X")`            |
| `unicode(cat)`         | Unicode property       | `Scrive("").unicode("Lu")`                     |

### Unicode Functions

| Function           | Description         | Pattern             |
| ------------------ | ------------------- | ------------------- |
| `unicode_letter()` | Any Unicode letter  | `\p{L}`             |
| `unicode_digit()`  | Any Unicode digit   | `\p{Nd}`            |
| `unicode_latin()`  | Latin script        | `\p{Latin}`         |
| `unicode_emoji()`  | Common emoji blocks | Complex alternation |

## Contributing

Contributions are welcome for:

- Additional common patterns
- Performance optimizations
- Better error messages
- Documentation improvements
- More Pythonic features
- Unicode property expansions
- Custom validator examples
- Pattern template libraries

## License

MIT License - feel free to use in your projects!

## Examples Converted to Scrive

Here are examples showing Scrive's Pythonic approach:

```python
from scrive import char, create_regexp, digit, exactly, maybe, one_or_more, word_char

# Typed capture groups
ID_RE = create_regexp(exactly("id-"), digit().times(5).grouped_as("id"))
groups = ID_RE.search("some id-23490 here we go").groupdict()
print(f"ID: {groups['id']}")  # Output: ID: 23490

# Quick-and-dirty semver
SEMVER_RE = create_regexp(
    one_or_more(digit()).grouped_as("major"),
    exactly("."),
    one_or_more(digit()).grouped_as("minor"),
    maybe(exactly("."), one_or_more(char()).grouped_as("patch")),
)

# Lookbehind assertion
result = create_regexp(exactly("foo/test.js").after("bar/")).test("bar/foo/test.js")
print(result)  # True

# References to previously captured groups
TENET_RE = create_regexp(
    word_char().grouped_as("firstChar"),
    word_char().grouped_as("secondChar"),
    one_or_more(char())
).reference_to("secondChar").reference_to("firstChar")

result2 = TENET_RE.test("TEN<==O==>NET")
print(result2)  # Complex palindrome-like pattern

# Pythonic operator usage
greeting = exactly("hello") + exactly(" ") + exactly("world")
choice = exactly("cat") | exactly("dog") | exactly("bird")

# Method chaining with snake_case
complex_pattern = (
    digit()
    .one_or_more()
    .grouped_as("number")
    .word_boundary()
    .ignore_case()
)
```

---

**Happy regex building with Scrive! 🐍✨**
