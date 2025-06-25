import re
from typing import Callable, Dict, List, Optional, Union


class Scrive:
    """
    A chainable regex pattern builder that supports method chaining
    and named capture groups. Pythonic interface for building complex regex patterns.
    """

    def __init__(self, pattern: str = "", flags: Union[int, "Scrive"] = 0):
        self._pattern = pattern
        if isinstance(flags, Scrive):
            self._flags = flags.flags
        else:
            self._flags = flags
        self._groups: Dict[str, int] = {}
        self._group_counter = 0

    @property
    def pattern(self) -> str:
        """Get the current regex pattern string."""
        return self._pattern

    @property
    def flags(self) -> int:
        """Get the current regex flags."""
        return self._flags

    def __str__(self) -> str:
        return self._pattern

    def __repr__(self) -> str:
        return f"Scrive('{self._pattern}')"

    def __bool__(self) -> bool:
        """Support bool() for checking if pattern is empty."""
        return bool(self._pattern)

    def __len__(self) -> int:
        """Support len() for getting the length of the pattern."""
        return len(self._pattern)

    def __add__(self, other: Union["Scrive", str]) -> "Scrive":
        """Support + operator for combining patterns."""
        return self.and_(other)

    def __or__(self, other: Union["Scrive", str]) -> "Scrive":
        """Support | operator for alternation."""
        return self.or_(other)

    def copy(self) -> "Scrive":
        """Create a copy of the current Scrive object."""
        result = Scrive(self._pattern, self._flags)
        result._groups = self._groups.copy()
        result._group_counter = self._group_counter
        return result

    # Combination methods
    def and_(self, *others: Union["Scrive", str]) -> "Scrive":
        """Combine patterns with logical AND (concatenation)."""
        result = self.copy()
        for other in others:
            if isinstance(other, Scrive):
                result._pattern += other.pattern
            else:
                if other is None:
                    raise TypeError(
                        "Cannot concatenate pattern with None. Use a string or another Scrive pattern instead."
                    )
                result._pattern += str(re.escape(other))
        return result

    def or_(self, *others: Union["Scrive", str]) -> "Scrive":
        """Combine patterns with logical OR."""
        patterns = [self._pattern]
        for other in others:
            if isinstance(other, Scrive):
                patterns.append(other.pattern)
            else:
                if other is None:
                    raise TypeError(
                        "Cannot create alternation with None. Use a string or another Scrive pattern instead."
                    )
                patterns.append(re.escape(str(other)))

        # Optimize common alternation patterns
        combined = self._optimize_alternation(patterns)
        result = Scrive(combined, self._flags)
        return result

    # Raw regex support
    def raw(self, regex: str) -> "Scrive":
        """Inject raw regex pattern without escaping."""
        result = self.copy()
        result._pattern += regex
        return result

    # Negation support
    def invert(self) -> "Scrive":
        """Invert/negate the pattern (works best with character classes)."""
        result = self.copy()

        # Handle character classes
        if (
            self._pattern.startswith("[")
            and self._pattern.endswith("]")
            and not self._pattern.startswith("[^")
        ):
            # Convert [abc] to [^abc]
            inner = self._pattern[1:-1]
            result._pattern = f"[^{inner}]"
        elif self._pattern.startswith("[^") and self._pattern.endswith("]"):
            # Convert [^abc] to [abc]
            inner = self._pattern[2:-1]
            result._pattern = f"[{inner}]"
        else:
            # For other patterns, use negative lookahead
            result._pattern = f"(?!{self._pattern})"

        return result

    # Inline comments for VERBOSE mode
    def comment(self, text: str) -> "Scrive":
        """Add inline comment (requires VERBOSE flag)."""
        result = self.copy()
        if not (self._flags & re.VERBOSE):
            self.verbose()
        result._pattern = f"{self._pattern} #{text} "
        return result

    # Case transformation
    def case_insensitive_group(self) -> "Scrive":
        """Wrap pattern in case-insensitive group (?i:...)."""
        result = self.copy()
        result._pattern = f"(?i:{self._pattern})"
        return result

    def case_sensitive_group(self) -> "Scrive":
        """Wrap pattern in case-sensitive group (?-i:...)."""
        result = self.copy()
        result._pattern = f"(?-i:{self._pattern})"
        return result

    # Unicode properties
    def unicode(self, category: str) -> "Scrive":
        """Add Unicode property pattern \\p{category}."""
        result = self.copy()
        unicode_pattern = f"\\p{{{category}}}"
        result._pattern += unicode_pattern
        return result

    # Pattern templating
    def template(self, **kwargs: Union[str, "Scrive"]) -> "Scrive":
        """Interpolate named subpatterns safely."""
        result = self.copy()
        pattern = self._pattern
        for name, value in kwargs.items():
            placeholder = f"{{{name}}}"
            if isinstance(value, Scrive):
                replacement = value.pattern
            else:
                replacement = re.escape(str(value))
            pattern = pattern.replace(placeholder, replacement)

        result._pattern = pattern
        return result

    # Quantifiers
    def times(self, count: Union[int, tuple]) -> "Scrive":
        """Apply quantifier `{n}` or `{n,m}` to the pattern."""
        if isinstance(count, int):
            return self._apply_quantifier(f"{{{count}}}", count_values=(count,))
        elif isinstance(count, tuple) and len(count) == 2:
            return self.between(count[0], count[1])
        else:
            raise ValueError(
                f"Count must be int or tuple of two ints, got {type(count).__name__}: {count}"
            )

    def one_or_more(self) -> "Scrive":
        """Apply + quantifier (one or more)."""
        result = self.copy()
        if self._needs_grouping_for_quantifier():
            result._pattern = f"(?:{self._pattern})+"
        else:
            result._pattern = f"{self._pattern}+"
        return result

    def zero_or_more(self) -> "Scrive":
        """Apply * quantifier (zero or more)."""
        result = self.copy()
        if self._needs_grouping_for_quantifier():
            result._pattern = f"(?:{self._pattern})*"
        else:
            result._pattern = f"{self._pattern}*"
        return result

    def maybe(self) -> "Scrive":
        """Apply ? quantifier (zero or one)."""
        result = self.copy()
        if self._needs_grouping_for_quantifier():
            result._pattern = f"(?:{self._pattern})?"
        else:
            result._pattern = f"{self._pattern}?"
        return result

    def at_least(self, n: int) -> "Scrive":
        """Apply `{n,}` quantifier (at least n)."""
        return self._apply_quantifier(f"{{{n},}}", count_values=(n,))

    def at_most(self, n: int) -> "Scrive":
        """Apply `{,n}` quantifier (at most n)."""
        return self._apply_quantifier(f"{{,{n}}}", count_values=(n,))

    def between(self, min: int, max: int) -> "Scrive":
        """Apply `{min,max}` quantifier."""
        return self._apply_quantifier(f"{{{min},{max}}}", count_values=(min, max))

    def _apply_quantifier(self, quantifier: str, count_values: tuple) -> "Scrive":
        """Helper method to apply quantifiers with validation."""
        # Validate counts are non-negative
        for count in count_values:
            if count < 0:
                raise ValueError(f"Quantifier count must be non-negative, got {count}")

        # Validate min <= max for ranges
        if len(count_values) == 2 and count_values[0] > count_values[1]:
            raise ValueError(
                f"Min count ({count_values[0]}) cannot be greater than max count ({count_values[1]})"
            )

        result = self.copy()
        # Apply quantifier with grouping if needed
        if self._needs_grouping_for_quantifier():
            result._pattern = f"(?:{self._pattern}){quantifier}"
        else:
            result._pattern = f"{self._pattern}{quantifier}"

        return result

    # Lazy quantifiers
    def lazy(self) -> "Scrive":
        """Make the previous quantifier lazy (non-greedy)."""
        result = self.copy()
        if self._pattern.endswith(("+", "*", "?", "}")):
            result._pattern = f"{self._pattern}?"
        return result

    # Grouping
    def grouped_as(self, name: str) -> "Scrive":
        """Create a named capture group."""
        result = self.copy()
        result._pattern = f"(?P<{name}>{self._pattern})"
        return result

    def group(self, name: Optional[str] = None) -> "Scrive":
        """Create a capture group (named if name provided)."""
        if name:
            return self.grouped_as(name)
        else:
            result = self.copy()
            result._pattern = f"({self._pattern})"
            return result

    def non_capturing_group(self) -> "Scrive":
        """Create a non-capturing group."""
        result = self.copy()
        result._pattern = f"(?:{self._pattern})"
        return result

    # References
    def reference_to(self, group_name: str) -> "Scrive":
        """Create a backreference to a named group."""
        result = self.copy()
        ref_pattern = f"(?P={group_name})"
        result._pattern = f"{self._pattern}{ref_pattern}"
        return result

    def ref(self, group_number: int) -> "Scrive":
        """Create a backreference to a numbered group."""
        result = self.copy()
        ref_pattern = f"\\{group_number}"
        result._pattern = f"{self._pattern}{ref_pattern}"
        return result

    # Assertions
    def after(self, pattern: Union["Scrive", str]) -> "Scrive":
        """Positive lookbehind assertion."""
        lookbehind = pattern.pattern if isinstance(pattern, Scrive) else str(pattern)
        result = self.copy()
        result._pattern = f"(?<={lookbehind}){self._pattern}"
        return result

    def before(self, pattern: Union["Scrive", str]) -> "Scrive":
        """Positive lookahead assertion."""
        lookahead = pattern.pattern if isinstance(pattern, Scrive) else str(pattern)
        result = self.copy()
        result._pattern = f"{self._pattern}(?={lookahead})"
        return result

    def not_after(self, pattern: Union["Scrive", str]) -> "Scrive":
        """Negative lookbehind assertion."""
        lookbehind = pattern.pattern if isinstance(pattern, Scrive) else str(pattern)
        result = self.copy()
        result._pattern = f"(?<!{lookbehind}){self._pattern}"
        return result

    def not_before(self, pattern: Union["Scrive", str]) -> "Scrive":
        """Negative lookahead assertion."""
        lookahead = pattern.pattern if isinstance(pattern, Scrive) else str(pattern)
        result = self.copy()
        result._pattern = f"{self._pattern}(?!{lookahead})"
        return result

    # Anchors
    def start_of_string(self) -> "Scrive":
        """Add start of string anchor `^`."""
        result = self.copy()
        result._pattern = f"^{self._pattern}"
        return result

    def end_of_string(self) -> "Scrive":
        """Add end of string anchor `$`."""
        result = self.copy()
        result._pattern = f"{self._pattern}$"
        return result

    def anchor_string(self) -> "Scrive":
        """Add start and end of string anchors `^` and `$`."""
        result = self.copy()
        result._pattern = f"^{self._pattern}$"
        return result

    def start_of_line(self) -> "Scrive":
        """Add start of line anchor `^` (requires MULTILINE flag)."""
        result = self.copy()
        result._pattern = f"^{self._pattern}"
        result._flags |= re.MULTILINE
        return result

    def end_of_line(self) -> "Scrive":
        """Add end of line anchor `$` (requires MULTILINE flag)."""
        result = self.copy()
        result._pattern = f"{self._pattern}$"
        result._flags |= re.MULTILINE
        return result

    def anchor_line(self) -> "Scrive":
        """Add start and end of line anchors `^` and `$` (requires MULTILINE flag)."""
        result = self.copy()
        result._pattern = f"^{self._pattern}$"
        result._flags |= re.MULTILINE
        return result

    def word_boundary(self) -> "Scrive":
        """Add word boundary assertion."""
        result = self.copy()
        result._pattern = f"\\b{self._pattern}\\b"
        return result

    def non_word_boundary(self) -> "Scrive":
        """Add non-word boundary assertion."""
        result = self.copy()
        result._pattern = f"\\B{self._pattern}\\B"
        return result

    # Flags
    def ignore_case(self) -> "Scrive":
        """Add case-insensitive flag."""
        result = self.copy()
        result._flags |= re.IGNORECASE
        return result

    def multiline(self) -> "Scrive":
        """Add multiline flag."""
        result = self.copy()
        result._flags |= re.MULTILINE
        return result

    def dot_all(self) -> "Scrive":
        """Add dotall flag (`.` matches newlines)."""
        result = self.copy()
        result._flags |= re.DOTALL
        return result

    def verbose(self) -> "Scrive":
        """Add verbose flag for readable regex."""
        result = self.copy()
        result._flags |= re.VERBOSE
        return result

    # Compilation and testing
    def compile(self) -> re.Pattern[str]:
        """Compile the pattern to a regex object."""
        return re.compile(self._pattern, self._flags)

    def test(self, text: str) -> bool:
        """Test if the pattern matches the text (substring search)."""
        return bool(self.compile().search(text))

    def match(self, text: str) -> Optional[re.Match]:
        """Match the pattern against the text from the beginning."""
        return self.compile().match(text)

    def full_match(self, text: str) -> Optional[re.Match]:
        """Match the pattern against the entire text (exact match)."""
        return self.compile().fullmatch(text)

    def exact_match(self, text: str) -> bool:
        """Test if the pattern matches the entire text exactly."""
        return bool(self.compile().fullmatch(text))

    def search(self, text: str) -> Optional[re.Match]:
        """Search for the pattern in the text."""
        return self.compile().search(text)

    def find_all(self, text: str) -> List[str]:
        """Find all matches of the pattern in the text."""
        return self.compile().findall(text)

    def split(self, text: str, maxsplit: int = 0) -> List[str]:
        """Split text by the pattern."""
        return self.compile().split(text, maxsplit)

    def sub(self, repl: Union[str, Callable], text: str, count: int = 0) -> str:
        """Replace matches with replacement string or function."""
        compiled = self.compile()
        if callable(repl):
            return compiled.sub(repl, text, count)
        return compiled.sub(repl, text, count)

    def separated_by(self, separator: "Scrive", count: int) -> "Scrive":
        """Create pattern with this element repeated 'count' times, separated by 'separator'.

        Example: digit().separated_by(exactly("."), 4) creates "(?:digit\\.){3}digit"

        Args:
            separator: The separator pattern between elements
            count: Number of times to repeat this element (must be >= 1)

        Returns:
            New Scrive object with the alternating pattern
        """
        if count < 1:
            raise ValueError("count must be at least 1")

        if count == 1:
            return Scrive(self.pattern)

        # Optimize pattern: (element + separator){count-1} + element
        element_plus_separator = Scrive(
            self.pattern + separator.pattern
        ).non_capturing_group()
        repeated_part = element_plus_separator.times(count - 1)
        final_element = Scrive(self.pattern)

        result = repeated_part + final_element
        return result

    def _needs_grouping_for_quantifier(self) -> bool:
        """Check if pattern needs grouping for quantifiers using regex detection."""
        import re as regex_module

        # Always group if contains unescaped alternation
        if regex_module.search(r"(^|[^\\])\|", self._pattern):
            return True

        # Always group if contains anchors (^ at start or $ at end, not escaped)
        if regex_module.search(r"^\^|(?<!\\)\$$", self._pattern):
            return True

        # Always group if pattern already ends with quantifiers to avoid "multiple repeat" errors
        # Matches: +, *, ?, {n}, {n,}, {,n}, {n,m}, and their lazy variants (+?, *?, ??, {n}?, etc.)
        if regex_module.search(r"[+*?]\??$|\}\??$", self._pattern):
            return True

        # Don't group if pattern is already a complete group
        # Full group patterns: (?P<name>...), (?:...), (?=...), (?!...), (?<=...), (?<!...)
        if regex_module.match(r"^\(\?(?:P<[^>]+>|[:=!]|<[=!])[^)]*\)$", self._pattern):
            return False

        # Don't group simple atomic patterns
        # Single escaped character: \d, \w, \s, \., etc.
        if regex_module.match(r"^\\[a-zA-Z.\d]$", self._pattern):
            return False

        # Single character class: [abc], [0-9], [^a-z], etc. (balanced brackets)
        if regex_module.match(r"^\[[^\[\]]*\]$", self._pattern):
            return False

        # Single literal character (escaped or unescaped, not special regex chars)
        if regex_module.match(r"^(\\.|[^\\()[\]{}+*?|^$])$", self._pattern):
            return False

        # Check for multiple atomic units that would need grouping
        # Count regex atoms: escaped chars, char classes, groups, literals
        atom_pattern = r"\\[a-zA-Z.\d]|\[[^\]]*\]|\([^)]*\)|[^\\()[\]{}+*?|^$]"
        atoms = regex_module.findall(atom_pattern, self._pattern)

        # If we have multiple atoms, or the pattern contains regex metacharacters, group it
        if len(atoms) > 1 or regex_module.search(r"[(){}+*?|^$]", self._pattern):
            return True

        return False

    def _optimize_alternation(self, patterns: list) -> str:
        """Optimize alternation patterns automatically using regex parsing."""
        if len(patterns) <= 1:
            return patterns[0] if patterns else ""

        # Regex patterns for different types of patterns
        char_class_pattern = re.compile(r"^\[([^\]]+)\]$")  # [abc], [a-z], etc.
        negated_char_class_pattern = re.compile(r"^\[\^([^\]]+)\]$")  # [^abc]
        nested_alternation_pattern = re.compile(r"^\(\?\:(.*)\)$")  # (?:a|b|c)
        single_char_pattern = re.compile(r"^[^.*+?^${}()|[\]\\]$")  # Single safe char
        escape_sequence_pattern = re.compile(r"^\\[dwstnr]$")  # \d, \w, \s, \t, \n, \r

        # First, flatten any nested alternations
        flattened_patterns = []
        for pattern in patterns:
            nested_match = nested_alternation_pattern.match(pattern)
            if nested_match:
                # Extract and split the inner alternation
                inner = nested_match.group(1)
                inner_patterns = self._split_alternation_regex(inner)
                flattened_patterns.extend(inner_patterns)
            else:
                flattened_patterns.append(pattern)

        # Categorize patterns for optimization
        char_class_chars = []
        other_patterns = []

        for pattern in flattened_patterns:
            char_class_match = char_class_pattern.match(pattern)
            if char_class_match and not negated_char_class_pattern.match(pattern):
                # Extract characters from character class
                char_class_chars.append(char_class_match.group(1))
            elif single_char_pattern.match(pattern):
                # Single safe character
                char_class_chars.append(pattern)
            elif escape_sequence_pattern.match(pattern):
                # Common escape sequences that can go in character classes
                char_class_chars.append(pattern)
            else:
                other_patterns.append(pattern)

        # Build optimized result
        if char_class_chars:
            all_chars = "".join(char_class_chars)

            if not other_patterns:
                # Only character class compatible patterns
                if len(char_class_chars) == 1 and len(all_chars) == 1:
                    return all_chars  # Single character, no brackets needed
                else:
                    return f"[{all_chars}]"
            else:
                # Mix of character class and other patterns
                merged_char_class = f"[{all_chars}]"
                all_patterns = [merged_char_class] + other_patterns
                return f"(?:{'|'.join(all_patterns)})"

        # No optimization possible
        return f"(?:{'|'.join(flattened_patterns)})"

    def _split_alternation_regex(self, pattern: str) -> list:
        """Split alternation pattern using regex-aware parsing."""
        # Use regex to split on | while respecting groups and character classes
        parts = []
        current = ""
        depth = 0
        in_char_class = False
        i = 0

        while i < len(pattern):
            char = pattern[i]

            if char == "\\" and i + 1 < len(pattern):
                # Escaped character - take both chars
                current += pattern[i : i + 2]
                i += 2
                continue
            elif char == "[" and not in_char_class:
                in_char_class = True
            elif char == "]" and in_char_class:
                in_char_class = False
            elif char == "(" and not in_char_class:
                depth += 1
            elif char == ")" and not in_char_class:
                depth -= 1
            elif char == "|" and depth == 0 and not in_char_class:
                # Top-level alternation separator
                if current.strip():
                    parts.append(current.strip())
                current = ""
                i += 1
                continue

            current += char
            i += 1

        if current.strip():
            parts.append(current.strip())

        return parts
