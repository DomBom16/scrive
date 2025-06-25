# Scrive Enhancement Features

This document provides a comprehensive overview of all enhancement features added to the Scrive regex pattern builder library. These enhancements were designed to address common regex pain points and provide more powerful, Pythonic ways to work with regular expressions.

## Table of Contents

1. [Raw Regex Support](#raw-regex-support)
2. [Pattern Negation](#pattern-negation)
3. [Chained Text Transformations](#chained-text-transformations)
4. [Inline Comments](#inline-comments)
5. [Numbered Backreferences](#numbered-backreferences)
6. [Case Transformation Groups](#case-transformation-groups)
7. [Unicode Property Support](#unicode-property-support)
8. [Custom Validators](#custom-validators)
9. [Pattern Templating](#pattern-templating)
10. [Builder Introspection](#builder-introspection)
11. [Pattern Copying](#pattern-copying)
12. [Advanced Text Processing](#advanced-text-processing)

---

## Raw Regex Support

**Methods:** `.raw(regex_string)`

**Problem Solved:** Sometimes you need to inject complex regex patterns that are difficult or impossible to express fluently with Scrive's API, such as complex lookaheads, advanced Unicode properties, or performance-critical patterns.

**Solution:** The `raw()` method allows you to inject raw regex strings directly into your pattern without escaping.

### Examples

```python
from scrive import exactly, digit, any_char

# Complex password validation with multiple lookaheads
password_pattern = (
    any_char()
    .raw(r"(?=.*[a-z])")      # Must contain lowercase
    .raw(r"(?=.*[A-Z])")      # Must contain uppercase
    .raw(r"(?=.*\d)")         # Must contain digit
    .raw(r"(?=.*[@$!%*?&])")  # Must contain special char
    .between(8, 128)
)

# Mix Scrive patterns with raw regex for log parsing
log_pattern = (
    exactly("[")
    .raw(r"\d{4}-\d{2}-\d{2}")  # ISO date (faster than digit().times())
    .exactly(" ")
    .raw(r"\d{2}:\d{2}:\d{2}")  # Time format
    .exactly("] ")
    .and_(any_char().one_or_more())
)
```

**Use Cases:**
- Performance-critical patterns where hand-tuned regex is needed
- Complex lookaheads/lookbehinds that are verbose in fluent API
- Integration with existing regex patterns
- Unicode properties not yet supported by convenience methods

---

## Pattern Negation

**Methods:** `.invert()`, `.negated()`

**Problem Solved:** Creating negated patterns (especially character classes) often requires manual regex knowledge and is error-prone.

**Solution:** Automatic pattern inversion with intelligent handling of different pattern types.

### Examples

```python
from scrive import char, email, digit

# Character class inversion (most common use case)
vowels = char("aeiouAEIOU")
consonants = vowels.invert()  # Becomes [^aeiouAEIOU]

print(consonants.test("b"))  # True
print(consonants.test("a"))  # False

# Complex pattern negation using negative lookahead
number_pattern = digit().one_or_more()
not_number = number_pattern.invert()  # Becomes (?!\d+)

# Real-world example: matching non-email text
email_pattern = email()
non_email_text = email_pattern.negated()
```

**Intelligent Behavior:**
- Character classes `[abc]` → `[^abc]`
- Negated character classes `[^abc]` → `[abc]`
- Complex patterns → Wrapped in negative lookahead `(?!pattern)`

**Use Cases:**
- Input validation (what NOT to accept)
- Text filtering and sanitization
- Complementary pattern matching
- Form validation with exclusion rules

---

## Chained Text Transformations

**Methods:** `.replace()`, `.remove()`, `.regex_sub()`, `.chain_sub()`, `.apply_transformations()`

**Problem Solved:** Text processing often requires multiple transformation steps. Traditional regex requires multiple separate calls or complex single patterns.

**Solution:** Chainable transformation methods that can be applied as a pipeline to input text.

### Examples

```python
from scrive import Scrive, digit

# HTML entity cleanup pipeline
cleanup_chain = (
    Scrive("")
    .replace("&amp;", "&")
    .replace("&lt;", "<")
    .replace("&gt;", ">")
    .replace("  ", " ")          # Multiple spaces to single
    .remove("SPAM")
    .remove("ADVERTISEMENT")
)

dirty_text = "&lt;p&gt;Hello &amp; welcome!  SPAM  content ADVERTISEMENT."
clean_text = cleanup_chain.apply_transformations(dirty_text)
# Result: "<p>Hello & welcome! content ."

# Phone number formatting with regex
phone_formatter = Scrive("").regex_sub(r"(\d{3})(\d{3})(\d{4})", r"(\1) \2-\3")
formatted = phone_formatter.apply_transformations("Call 5551234567")
# Result: "Call (555) 123-4567"

# Multi-step processing
multi_processor = (
    Scrive("")
    .regex_sub(r"(\d{3})(\d{3})(\d{4})", r"(\1) \2-\3")    # Format phones
    .regex_sub(r"\b(\w+)@(\w+)\.com\b", r"[\1 AT \2]")      # Obfuscate emails
    .replace("sensitive", "[REDACTED]")                      # Remove sensitive data
)
```

**Transformation Types:**
- **String replacement:** `.replace(old, new)` - Simple string substitution
- **Pattern removal:** `.remove(pattern)` - Remove matching patterns
- **Regex substitution:** `.regex_sub(pattern, replacement)` - Full regex find/replace
- **Pattern-based substitution:** `.chain_sub(replacement)` - Use current pattern for replacement

**Use Cases:**
- Data sanitization pipelines
- Text normalization for processing
- Log file cleaning and formatting
- Email/phone number formatting
- HTML/XML entity processing

---

## Inline Comments

**Methods:** `.comment(text)`, `.verbose()`

**Problem Solved:** Complex regex patterns are notoriously hard to read and maintain. Comments help with documentation but require verbose mode.

**Solution:** Easy inline commenting that automatically enables verbose mode when needed.

### Examples

```python
from scrive import digit, exactly, char

# Credit card pattern with explanatory comments
credit_card = (
    digit().times(4).comment("First 4 digits")
    .and_(char(" -").maybe()).comment("Optional separator")
    .and_(digit().times(4)).comment("Second group")
    .and_(char(" -").maybe()).comment("Optional separator")
    .and_(digit().times(4)).comment("Third group")
    .and_(char(" -").maybe()).comment("Optional separator")
    .and_(digit().times(4)).comment("Last 4 digits")
    .verbose()  # Enable verbose mode for comments
)

# Generated pattern includes comments:
# \d{4}  # First 4 digits
# [\s-]?  # Optional separator
# \d{4}  # Second group
# ... etc

# Complex validation with step-by-step comments
email_validator = (
    word_char().one_or_more().comment("Username part")
    .and_(exactly("@")).comment("At symbol")
    .and_(word_char().one_or_more()).comment("Domain name")
    .and_(exactly(".")).comment("Dot")
    .and_(letter().between(2, 6)).comment("TLD (2-6 letters)")
    .verbose()
)
```

**Behavior:**
- Comments only appear when `.verbose()` flag is set
- Without verbose mode, `.comment()` calls are ignored
- Enables better code documentation and maintenance
- Comments appear in the final regex pattern for debugging

**Use Cases:**
- Complex business logic patterns
- Team collaboration and code reviews
- Educational/training regex examples
- Debugging complex patterns
- Documentation of pattern requirements

---

## Numbered Backreferences

**Methods:** `.ref(group_number)`

**Problem Solved:** While Scrive supports named backreferences, sometimes you need to reference numbered groups, especially when working with existing patterns or certain regex engines.

**Solution:** Simple numbered backreference method with automatic escaping.

### Examples

```python
from scrive import word_char, exactly, any_char

# Simple palindrome detector (4 characters)
palindrome_4 = (
    word_char().group()        # Group 1: first character
    .and_(word_char().group()) # Group 2: second character
    .ref(2)                    # Reference group 2
    .ref(1)                    # Reference group 1
)

print(palindrome_4.exact_match("abba"))  # True
print(palindrome_4.exact_match("deed"))  # True
print(palindrome_4.exact_match("test"))  # False

# HTML tag matching with numbered groups
html_tag = (
    exactly("<")
    .and_(word_char().one_or_more().group())  # Group 1: tag name
    .and_(exactly(">"))
    .and_(any_char().zero_or_more())          # Content
    .and_(exactly("</"))
    .ref(1)                                   # Reference same tag name
    .and_(exactly(">"))
)

print(html_tag.test("<div>content</div>"))   # True
print(html_tag.test("<div>content</span>"))  # False

# Repeated word detection
repeated_word = (
    word_char().one_or_more().group()  # Group 1: word
    .and_(exactly(" "))
    .ref(1)                            # Same word again
)

print(repeated_word.test("hello hello"))  # True
print(repeated_word.test("hello world"))  # False
```

**Comparison with Named References:**
```python
# Named reference approach
named_pattern = (
    word_char().one_or_more().grouped_as("word")
    .and_(exactly(" "))
    .reference_to("word")
)

# Numbered reference approach
numbered_pattern = (
    word_char().one_or_more().group()  # Automatically group 1
    .and_(exactly(" "))
    .ref(1)
)
```

**Use Cases:**
- Palindrome detection
- Repeated element validation
- HTML/XML tag matching
- Quote matching (same quote type)
- Pattern symmetry validation

---

## Case Transformation Groups

**Methods:** `.case_insensitive_group()`, `.case_sensitive_group()`

**Problem Solved:** Sometimes you need fine-grained control over case sensitivity within different parts of a pattern, beyond the global `ignore_case()` flag.

**Solution:** Group-level case sensitivity control using inline modifiers.

### Examples

```python
from scrive import letter, digit

# Username: case-insensitive letters, case-sensitive numbers
username_pattern = (
    letter()
    .case_insensitive_group()          # Username can be any case
    .between(3, 20)
    .case_sensitive_group()            # Back to case sensitive
    .and_(digit().one_or_more().maybe()) # Numbers are case sensitive
)

# Protocol detection: case-insensitive protocol, case-sensitive path
url_pattern = (
    exactly("http")
    .case_insensitive_group()          # HTTP, Http, http all work
    .maybe(exactly("s"))               # Optional 's'
    .and_(exactly("://"))
    .case_sensitive_group()            # Path is case sensitive
    .and_(any_char().one_or_more())
)

# Product codes: case-insensitive prefix, case-sensitive ID
product_code = (
    exactly("PROD")
    .case_insensitive_group()          # prod, PROD, Prod all work
    .and_(exactly("-"))
    .case_sensitive_group()            # ID part is case sensitive
    .and_(alphanumeric().times(8))
)
```

**Generated Patterns:**
- `.case_insensitive_group()` → `(?i:pattern)`
- `.case_sensitive_group()` → `(?-i:pattern)`

**Use Cases:**
- Mixed case requirements in business rules
- Protocol/scheme matching with case-insensitive headers
- Product codes with mixed case sensitivity
- Legacy system integration with specific case rules
- User input normalization

---

## Unicode Property Support

**Functions:** `unicode_category()`, `unicode_script()`, `unicode_block()`, and convenience functions

**Problem Solved:** Working with international text requires proper Unicode support. Raw Unicode property syntax is complex and hard to remember.

**Solution:** Comprehensive Unicode property support with easy-to-use functions and extensive convenience methods.

### Examples

```python
# Basic Unicode categories
from scrive import unicode_category, unicode_script, unicode_letter

# Match any Unicode letter (not just ASCII)
any_letter = unicode_category("L")  # \p{L}
uppercase_only = unicode_category("Lu")  # \p{Lu}

# Script-specific matching
chinese_text = unicode_script("Han")      # Chinese characters
arabic_text = unicode_script("Arabic")    # Arabic script
latin_text = unicode_script("Latin")      # Latin script

# International username validation
international_username = (
    unicode_letter()           # Any Unicode letter
    .one_or_more()
    .and_(unicode_digit().zero_or_more())  # Optional Unicode digits
    .between(3, 20)
)

# Multi-script text detection
mixed_script = (
    unicode_latin().one_or_more()         # Latin text
    .and_(unicode_whitespace())           # Space
    .and_(unicode_han().one_or_more())    # Chinese text
)

# Emoji detection (basic approach)
emoji_pattern = unicode_emoji()

# Currency symbol matching
currency = unicode_category("Sc")  # Currency symbols: $, €, ¥, etc.

# Math symbol detection
math_symbols = unicode_category("Sm")  # +, -, =, ∑, ∫, etc.
```

**Available Categories:**
- **Letters:** `L`, `Lu` (uppercase), `Ll` (lowercase), `Lt` (titlecase), etc.
- **Numbers:** `N`, `Nd` (decimal), `Nl` (letter), `No` (other)
- **Punctuation:** `P`, `Pc` (connector), `Pd` (dash), `Ps` (open), etc.
- **Symbols:** `S`, `Sm` (math), `Sc` (currency), `So` (other)
- **Separators:** `Z`, `Zs` (space), `Zl` (line), `Zp` (paragraph)
- **Marks:** `M`, `Mn` (non-spacing), `Mc` (spacing combining)
- **Other:** `C`, `Cc` (control), `Cf` (format), `Co` (private use)

**Convenience Functions:**
```python
# Instead of unicode_category("Lu")
unicode_uppercase()

# Instead of unicode_script("Latin")
unicode_latin()

# Instead of complex emoji block matching
unicode_emoji()
```

**Use Cases:**
- International applications
- Multi-language text processing
- Proper name validation across cultures
- Currency and financial applications
- Mathematical/scientific text processing
- Social media applications with emoji support

---

## Custom Validators

**Methods:** `.where(validator_function)`

**Problem Solved:** Regex alone cannot express complex business logic. You often need additional validation beyond pattern matching.

**Solution:** Attach custom Python functions that validate matches against business rules.

### Examples

```python
from scrive import digit

# Age validation with business rules
def age_validator(match):
    try:
        age = int(match.group())
        return 13 <= age <= 120  # Reasonable age range
    except (ValueError, AttributeError):
        return False

age_pattern = digit().between(1, 3).where(age_validator)

print(age_pattern.test_with_validator("25"))   # True - valid age
print(age_pattern.test_with_validator("150"))  # False - too old
print(age_pattern.test_with_validator("5"))    # False - too young

# Credit card validation with Luhn algorithm
def luhn_validator(match):
    """Validate credit card using Luhn algorithm."""
    number = match.group().replace(" ", "").replace("-", "")
    if not number.isdigit() or len(number) != 16:
        return False

    # Luhn algorithm implementation
    total = 0
    reverse_digits = number[::-1]

    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:  # Every second digit
            n *= 2
            if n > 9:
                n = n // 10 + n % 10
        total += n

    return total % 10 == 0

cc_pattern = (
    digit().times(4).and_(char(" -").maybe())
    .and_(digit().times(4)).and_(char(" -").maybe())
    .and_(digit().times(4)).and_(char(" -").maybe())
    .and_(digit().times(4))
    .where(luhn_validator)
)

# Email domain validation
def domain_validator(match):
    email_text = match.group()
    allowed_domains = ["@company.com", "@partner.org", "@trusted.net"]
    return any(domain in email_text for domain in allowed_domains)

corporate_email = email().where(domain_validator)

# Date range validation
def date_range_validator(match):
    from datetime import datetime
    date_str = match.group()
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        # Only allow dates from last 5 years
        return date.year >= datetime.now().year - 5
    except ValueError:
        return False

recent_date = (
    digit().times(4).and_(exactly("-"))
    .and_(digit().times(2)).and_(exactly("-"))
    .and_(digit().times(2))
    .where(date_range_validator)
)
```

**Validator Function Signature:**
```python
def validator(match: re.Match) -> bool:
    """
    Args:
        match: The regex match object

    Returns:
        bool: True if the match is valid, False otherwise
    """
    pass
```

**Access Match Data:**
```python
def complex_validator(match):
    full_match = match.group()           # Full matched text
    groups = match.groups()              # All groups as tuple
    group_dict = match.groupdict()       # Named groups as dict
    group_1 = match.group(1)            # Specific numbered group
    named_group = match.group("name")    # Specific named group
    start, end = match.span()            # Match position

    # Your validation logic here
    return True
```

**Use Cases:**
- Financial data validation (Luhn algorithm, account numbers)
- Date/time business rules
- Geolocation validation (valid coordinates, postal codes)
- Custom format validation (SSN, tax IDs, etc.)
- Domain/allowlist validation
- Mathematical constraints (prime numbers, ranges, etc.)
- File format validation
- Business-specific rules

---

## Pattern Templating

**Methods:** `.template(**kwargs)`

**Problem Solved:** Creating similar patterns with slight variations leads to code duplication. You want to reuse pattern templates with different components.

**Solution:** Template patterns with placeholder substitution using Python's string formatting concepts.

### Examples

```python
from scrive import Scrive, word_char, digit, any_char, exactly

# SQL query template
sql_template = Scrive("SELECT {fields} FROM {table} WHERE {condition}")

# Fill template with patterns
sql_pattern = sql_template.template(
    fields=word_char().one_or_more().separated_by(exactly(", "), 3),
    table=word_char().one_or_more(),
    condition=word_char().one_or_more().and_(exactly(" = ")).and_(any_char().one_or_more())
)

# Test against actual SQL
test_sql = "SELECT name, email, age FROM users WHERE status = active"
print(sql_pattern.test(test_sql))  # True

# Configuration file template
config_template = Scrive("{section}.{key} = {value}")

config_pattern = config_template.template(
    section=word_char().one_or_more(),
    key=word_char().one_or_more(),
    value=any_char().one_or_more()
)

# API endpoint template
api_template = Scrive("/api/v{version}/{resource}/{id}")

api_pattern = api_template.template(
    version=digit(),
    resource=word_char().one_or_more(),
    id=digit().one_or_more()
)

# Log format template
log_template = Scrive("[{timestamp}] {level} {message}")

log_pattern = log_template.template(
    timestamp=digit().times(4).and_(exactly("-")).and_(digit().times(2)).and_(exactly("-")).and_(digit().times(2)),
    level=one_of("DEBUG", "INFO", "WARN", "ERROR", "FATAL"),
    message=any_char().one_or_more()
)

# Email template with validation
email_template = Scrive("{local}@{domain}.{tld}")

# Corporate email pattern
corporate_email = email_template.template(
    local=word_char().one_or_more(),
    domain=exactly("company"),  # Restrict to company domain
    tld=one_of("com", "org")    # Only certain TLDs
)

# Personal email pattern
personal_email = email_template.template(
    local=word_char().one_or_more(),
    domain=word_char().one_or_more(),
    tld=letter().between(2, 6)
)
```

**Template Substitution Rules:**
- **Scrive objects:** Pattern is inserted directly (no escaping)
- **Strings:** Automatically escaped for regex safety
- **Missing placeholders:** Left unchanged in the pattern

**Advanced Templating:**
```python
# Conditional templates
def create_phone_template(country_code=None):
    if country_code:
        template = Scrive("+{country} {area} {number}")
        return template.template(
            country=exactly(country_code),
            area=digit().times(3),
            number=digit().times(7)
        )
    else:
        template = Scrive("{area} {number}")
        return template.template(
            area=digit().times(3),
            number=digit().times(7)
        )

us_phone = create_phone_template("1")
local_phone = create_phone_template()

# Template factories
def create_id_template(prefix, id_length):
    template = Scrive("{prefix}-{id}")
    return template.template(
        prefix=exactly(prefix),
        id=digit().times(id_length)
    )

user_id = create_id_template("USER", 8)     # USER-12345678
order_id = create_id_template("ORDER", 10)  # ORDER-1234567890
```

**Use Cases:**
- API endpoint pattern families
- Configuration file format variations
- Database query pattern templates
- File naming convention patterns
- Protocol message format templates
- Multi-environment configuration (dev/staging/prod)
- Internationalization pattern variants
- A/B testing pattern variations

---

## Builder Introspection

**Methods:** `.steps()`, `.debug()`, `.describe()`

**Problem Solved:** Complex patterns can be hard to debug and understand. You need insight into how patterns were built and what they do.

**Solution:** Comprehensive introspection tools for debugging, documentation, and understanding pattern construction.

### Examples

```python
from scrive import digit, letter, exactly

# Build a complex pattern
complex_pattern = (
    digit().one_or_more().grouped_as("number")
    .and_(exactly("-"))
    .and_(letter().one_or_more().grouped_as("code"))
    .word_boundary()
    .ignore_case()
    .comment("Product code pattern")
)

# View build steps
steps = complex_pattern.steps()
print("Build steps:")
for i, step in enumerate(steps, 1):
    print(f"  {i}. {step}")

# Output:
# Build steps:
#   1. one_or_more()
#   2. grouped_as('number')
#   3. and_(-)
#   4. and_((?P<code>[a-zA-Z]+))
#   5. word_boundary()
#   6. ignore_case()
#   7. comment('Product code pattern')

# Get debug information
debug_info = complex_pattern.debug()
print(debug_info)

# Output:
# Pattern: \b(?P<number>\d+)\-(?P<code>[a-zA-Z]+)\b
# Flags: re.IGNORECASE
# Steps: one_or_more() -> grouped_as('number') -> and_(\-) -> word_boundary() -> ignore_case() -> comment('Product code pattern')
# Custom validator: No

# Get human-readable description
description = complex_pattern.describe()
print(description)

# Output:
# Pattern: \b(?P<number>\d+)\-(?P<code>[a-zA-Z]+)\b
# Description: [word boundary] ( [optional] P<number> [digit]  [one or more] ) \- ( [optional] P<code>[a-zA-Z] [one or more] ) [word boundary]

# Debugging pattern construction
email_pattern = (
    word_char().one_or_more()
    .and_(exactly("@"))
    .and_(word_char().one_or_more())
    .and_(exactly("."))
    .and_(letter().between(2, 6))
)

print("Email pattern steps:", email_pattern.steps())
print("Email pattern debug:", email_pattern.debug())

# Compare patterns
pattern1 = digit().one_or_more().ignore_case()
pattern2 = pattern1.copy().maybe().word_boundary()

print("Original pattern:", pattern1.debug())
print("Modified pattern:", pattern2.debug())
print("Original steps:", pattern1.steps())
print("Modified steps:", pattern2.steps())
```

**`.steps()` Output:**
Returns a list of method calls made during pattern construction:
```python
['one_or_more()', 'grouped_as("number")', 'and_("-")', 'word_boundary()']
```

**`.debug()` Output:**
Returns comprehensive debugging information:
```
Pattern: \b(?P<number>\d+)\-(?P<code>[a-zA-Z]+)\b
Flags: re.IGNORECASE
Steps: one_or_more() -> grouped_as('number') -> and_(\-) -> word_boundary() -> ignore_case()
Transformations: 2 queued
Custom validator: Yes
```

**`.describe()` Output:**
Returns human-readable pattern explanation:
```
Pattern: \d+@\w+\.\w{2,6}
Description: [digit] [one or more] @ [word character] [one or more] . [word character] {2,6}
```

**Use Cases:**
- Debugging complex pattern construction
- Code reviews and documentation
- Learning and teaching regex concepts
- Pattern optimization analysis
- Troubleshooting pattern matching issues
- API documentation generation
- Unit test failure analysis
- Pattern performance analysis

---

## Pattern Copying

**Methods:** `.copy()`

**Problem Solved:** You want to create variations of existing patterns without modifying the original. Immutable pattern building is safer for concurrent use.

**Solution:** Deep copy method that creates independent pattern instances.

### Examples

```python
from scrive import digit, word_char

# Create base pattern
base_pattern = digit().one_or_more().ignore_case()

# Create independent copy
copied_pattern = base_pattern.copy()

# Modify copy without affecting original
strict_pattern = copied_pattern.word_boundary().start_of_string().end_of_string()
loose_pattern = copied_pattern.maybe()

print("Base pattern:", base_pattern.pattern)      # \d+
print("Strict pattern:", strict_pattern.pattern)  # ^\b\d+\b$
print("Loose pattern:", loose_pattern.pattern)    # (?:\d+)?

# Copy preserves all attributes
complex_pattern = (
    word_char().one_or_more()
    .grouped_as("username")
    .ignore_case()
    .where(lambda m: len(m.group()) >= 3)
)

# Create variation
admin_pattern = complex_pattern.copy().and_(exactly("-admin"))

print("Original steps:", complex_pattern.steps())
print("Admin steps:", admin_pattern.steps())

# Both patterns work independently
print("Original validates 'john':", complex_pattern.test_with_validator("john"))
print("Admin validates 'john-admin':", admin_pattern.test_with_validator("john-admin"))
```

**What Gets Copied:**
- Pattern string
- Regex flags
- Build steps history
- Transformations queue
- Custom validators
- All internal state

**Thread Safety:**
```python
import threading

base_pattern = digit().one_or_more()

def create_variant(suffix):
    # Each thread gets independent copy
    variant = base_pattern.copy().and_(exactly(f"-{suffix}"))
    return variant

# Safe for concurrent use
thread1 = threading.Thread(target=lambda: create_variant("A"))
thread2 = threading.Thread(target=lambda: create_variant("B"))
```

**Use Cases:**
- Pattern variation creation
- Thread-safe pattern building
- Template pattern instances
- A/B testing pattern variants
- Progressive pattern enhancement
- Pattern inheritance hierarchies
- Safe pattern modification
- Concurrent pattern processing

---

## Advanced Text Processing

**Methods:** `.apply_transformations()`, `.regex_sub()`, `.chain_sub()`

**Problem Solved:** Complex text processing often requires multiple steps. Traditional approaches require multiple passes or complex single patterns.

**Solution:** Powerful text transformation pipeline with multiple processing strategies.

### Examples

```python
from scrive import Scrive, digit

# Data sanitization pipeline
sanitizer = (
    Scrive("")
    .replace("&", "&amp;")           # HTML encode ampersands
    .replace("<", "&lt;")            # HTML encode less-than
    .replace(">", "&gt;")            # HTML encode greater-than
    .regex_sub(r"\s+", " ")          # Normalize whitespace
    .regex_sub(r"^\s+|\s+$", "")     # Trim whitespace
    .remove("CONFIDENTIAL")          # Remove sensitive markers
    .regex_sub(r"\d{3}-\d{2}-\d{4}", "XXX-XX-XXXX")  # Mask SSNs
)

dirty_data = "  <script>CONFIDENTIAL 123-45-6789</script>  "
clean_data = sanitizer.apply_transformations(dirty_data)
# Result: "&lt;script&gt; XXX-XX-XXXX&lt;/script&gt;"

# Log processing pipeline
log_processor = (
    Scrive("")
    .regex_sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", "[TIMESTAMP]")  # Normalize timestamps
    .regex_sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[IP]")      # Mask IP addresses
    .replace("ERROR", "ERR")                                              # Shorten error levels
    .replace("WARNING", "WARN")                                           # Shorten warning levels
    .remove("
