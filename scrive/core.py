import re
from typing import Callable, Dict, List, Optional, Union


class Scrive:
    """
    A chainable regex pattern builder
    """

    def __init__(self, pattern: str = "", flags: Union[int, "Scrive"] = 0):
        self._pattern = pattern
        if isinstance(flags, Scrive):
            self._flags = flags.flags
        else:
            self._flags = flags

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
        return self._and(other)

    def __or__(self, other: Union["Scrive", str]) -> "Scrive":
        """Support | operator for alternation."""
        return self._or(other)

    def copy(self) -> "Scrive":
        """Create a copy of the current Scrive object."""
        result = Scrive(self._pattern, self._flags)
        return result

    # Combination methods
    def _and(self, *others: Union["Scrive", str]) -> "Scrive":
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

    def _or(self, *others: Union["Scrive", str]) -> "Scrive":
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

        char_class_pattern = re.compile(r"^\[([^\]]+)\]$")  # [abc], [a-z], etc.
        negated_char_class_pattern = re.compile(r"^\[\^([^\]]+)\]$")  # [^abc]

        # Handle character classes
        if char_class_pattern.match(self._pattern):
            # Convert [abc] to [^abc]
            inner = self._pattern[1:-1]
            result._pattern = f"[^{inner}]"
        elif negated_char_class_pattern.match(self._pattern):
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
    def times(self, n: int, m: Optional[int] = None) -> "Scrive":
        """Apply quantifier `{n}` or `{n,m}` to the pattern."""
        if m is None:
            # Single count: {n}
            return self._apply_quantifier(f"{{{n}}}", count_values=(n,))
        else:
            # Range: {min,max}
            return self.between(n, m)

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

    # Enhanced lazy quantifiers
    def maybe_lazy(self) -> "Scrive":
        """Apply ?? quantifier (lazy zero or one)."""
        result = self.copy()
        if self._needs_grouping_for_quantifier():
            result._pattern = f"(?:{self._pattern})??"
        else:
            result._pattern = f"{self._pattern}??"
        return result

    def one_or_more_lazy(self) -> "Scrive":
        """Apply +? quantifier (lazy one or more)."""
        result = self.copy()
        if self._needs_grouping_for_quantifier():
            result._pattern = f"(?:{self._pattern})+?"
        else:
            result._pattern = f"{self._pattern}+?"
        return result

    def zero_or_more_lazy(self) -> "Scrive":
        """Apply *? quantifier (lazy zero or more)."""
        result = self.copy()
        if self._needs_grouping_for_quantifier():
            result._pattern = f"(?:{self._pattern})*?"
        else:
            result._pattern = f"{self._pattern}*?"
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
    def reference(self, group: str | int) -> "Scrive":
        """Create a backreference to a named group."""
        result = self.copy()
        if isinstance(group, str):
            ref_pattern = f"(?P={group})"
        elif isinstance(group, int):
            ref_pattern = f"\\{group}"
        else:
            raise TypeError("group must be a string or an integer")
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

    # Enhanced lookahead/lookbehind methods with better names
    def followed_by(self, pattern: Union["Scrive", str]) -> "Scrive":
        """Positive lookahead assertion (alias for before)."""
        return self.before(pattern)

    def not_followed_by(self, pattern: Union["Scrive", str]) -> "Scrive":
        """Negative lookahead assertion (alias for not_before)."""
        return self.not_before(pattern)

    def preceded_by(self, pattern: Union["Scrive", str]) -> "Scrive":
        """Positive lookbehind assertion (alias for after)."""
        return self.after(pattern)

    def not_preceded_by(self, pattern: Union["Scrive", str]) -> "Scrive":
        """Negative lookbehind assertion (alias for not_after)."""
        return self.not_after(pattern)

    # Anchors
    def start_of_string(self) -> "Scrive":
        """Add start of string anchor `^`."""
        result = self.copy()
        result._pattern = f"^{self._pattern}"
        return result

    def anchor_both(self) -> "Scrive":
        """Add start and end of string anchors (alias for anchor_string)."""
        return self.anchor_string()

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

    def anchor_both_lines(self) -> "Scrive":
        """Add start and end of line anchors (alias for anchor_line)."""
        return self.anchor_line()

    def start_of_line(self) -> "Scrive":
        """Add start of line anchor `^` (requires MULTILINE flag)."""
        result = self.copy()
        result._pattern = f"^{self._pattern}"
        result._flags |= re.MULTILINE
        return result

    # Enhanced flag methods
    def case_insensitive(self) -> "Scrive":
        """Add case-insensitive flag (alias for ignore_case)."""
        return self.ignore_case()

    def case_sensitive(self) -> "Scrive":
        """Remove case-insensitive flag."""
        result = self.copy()
        result._flags &= ~re.IGNORECASE
        return result

    # Enhanced chaining methods
    def then(self, *others: Union["Scrive", str]) -> "Scrive":
        """Chain patterns together."""
        return self._and(*others)

    def or_else(self, *others: Union["Scrive", str]) -> "Scrive":
        """Create alternation."""
        return self._or(*others)

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

    def named(self, name: str) -> "Scrive":
        """Create named capture group (alias for grouped_as)."""
        return self.grouped_as(name)

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

    def replace(
        self, text: str, replacement: Union[str, Callable], count: int = 0
    ) -> str:
        """Replace matches in text with replacement (alias for sub)."""
        return self.sub(replacement, text, count)

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

        # Try recursive optimization - optimize parts first, then the whole
        recursively_optimized = self._optimize_recursively(flattened_patterns)
        if recursively_optimized != flattened_patterns:
            # If we optimized anything, check if it's a single result or multiple
            if len(recursively_optimized) == 1:
                return recursively_optimized[0]
            elif len(recursively_optimized) > 1:
                # Only recurse if patterns are still simple (no complex regex constructs)
                if all(self._is_simple_pattern(p) for p in recursively_optimized):
                    return self._optimize_alternation(recursively_optimized)
                else:
                    # Already optimized with complex constructs, just join them
                    return f"(?:{'|'.join(recursively_optimized)})"
            else:
                return ""

        # Try common prefix/suffix optimization
        prefix_suffix_optimized = self._optimize_common_parts(flattened_patterns)
        if prefix_suffix_optimized != f"(?:{'|'.join(flattened_patterns)})":
            return prefix_suffix_optimized

        # Categorize patterns for character class optimization
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

    def _optimize_alternation_no_char_class(self, patterns: list) -> str:
        """Optimize alternation patterns without applying character class optimization."""
        if len(patterns) <= 1:
            return patterns[0] if patterns else ""

        # Regex patterns for different types of patterns
        nested_alternation_pattern = re.compile(r"^\(\?\:(.*)\)$")  # (?:a|b|c)

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

        # Try common prefix/suffix optimization only
        prefix_suffix_optimized = self._optimize_common_parts(flattened_patterns)
        if prefix_suffix_optimized != f"(?:{'|'.join(flattened_patterns)})":
            return prefix_suffix_optimized

        # No optimization possible, just join them
        return f"(?:{'|'.join(flattened_patterns)})"

    def _optimize_recursively(self, patterns: list) -> list:
        """Apply various generic optimizations recursively."""
        if len(patterns) < 2:
            return patterns

        # Try suffix optimization (e.g., doc|docx -> docx?)
        suffix_optimized = self._optimize_optional_suffixes(patterns)
        if len(suffix_optimized) < len(patterns):
            return suffix_optimized

        # Try extracting common alternations from complex patterns
        nested_optimized = self._optimize_nested_alternations(patterns)
        if len(nested_optimized) < len(patterns):
            return nested_optimized

        return patterns

    def _optimize_optional_suffixes(self, patterns: list) -> list:
        """Optimize patterns with optional suffixes and common parts (e.g., jpg|jpeg -> jpe?g)."""
        if len(patterns) < 2:
            return patterns

        # First try advanced suffix optimization (like jpg|jpeg -> jpe?g)
        advanced_result = self._optimize_advanced_suffixes(patterns)
        if len(advanced_result) < len(patterns):
            return advanced_result

        # Then try simple suffix optimization (like doc|docx -> docx?)
        simple_result = self._optimize_simple_suffixes(patterns)
        if len(simple_result) < len(patterns):
            return simple_result

        return patterns

    def _optimize_advanced_suffixes(self, patterns: list) -> list:
        """Handle complex suffix patterns like jpg|jpeg -> jpe?g."""
        if len(patterns) < 2:
            return patterns

        optimizations = []
        used_indices = set()

        # Look for patterns that can be optimized with optional characters
        for i, pattern1 in enumerate(patterns):
            if i in used_indices:
                continue

            for j, pattern2 in enumerate(patterns[i + 1 :], i + 1):
                if j in used_indices:
                    continue

                # Find common prefix and see if one is an extension of the other
                common_prefix = self._find_common_prefix([pattern1, pattern2])
                if len(common_prefix) >= 2:  # Need meaningful common prefix
                    suffix1 = pattern1[len(common_prefix) :]
                    suffix2 = pattern2[len(common_prefix) :]

                    # Check for optional character patterns (like g vs eg)
                    optional_opt = self._create_optional_pattern(suffix1, suffix2)
                    if optional_opt:
                        optimized_pattern = common_prefix + optional_opt
                        optimizations.append((i, j, optimized_pattern))
                        used_indices.add(i)
                        used_indices.add(j)
                        break

        # Apply optimizations
        if optimizations:
            result = []
            for i, pattern in enumerate(patterns):
                if i not in used_indices:
                    result.append(pattern)

            for _, _, optimized_pattern in optimizations:
                result.append(optimized_pattern)

            return result

        return patterns

    def _optimize_simple_suffixes(self, patterns: list) -> list:
        """Handle simple suffix patterns like doc|docx -> docx?."""
        optimizations = []
        used_indices = set()

        for i, pattern1 in enumerate(patterns):
            if i in used_indices:
                continue

            for j, pattern2 in enumerate(patterns[i + 1 :], i + 1):
                if j in used_indices:
                    continue

                # Check if one pattern is the other plus a simple suffix
                if pattern1.startswith(pattern2) and len(pattern1) > len(pattern2):
                    suffix = pattern1[len(pattern2) :]
                    if len(suffix) <= 3:  # Simple suffix
                        optimizations.append((i, j, f"{pattern1}?"))
                        used_indices.add(i)
                        used_indices.add(j)
                        break
                elif pattern2.startswith(pattern1) and len(pattern2) > len(pattern1):
                    suffix = pattern2[len(pattern1) :]
                    if len(suffix) <= 3:  # Simple suffix
                        optimizations.append((i, j, f"{pattern2}?"))
                        used_indices.add(i)
                        used_indices.add(j)
                        break

        # Apply optimizations
        if optimizations:
            result = []
            for i, pattern in enumerate(patterns):
                if i not in used_indices:
                    result.append(pattern)

            for _, _, optimized_pattern in optimizations:
                result.append(optimized_pattern)

            return result

        return patterns

    def _find_common_prefix(self, patterns: list) -> str:
        """Find the common prefix of a list of patterns."""
        if not patterns:
            return ""

        min_len = min(len(p) for p in patterns)
        common_prefix = ""

        for i in range(min_len):
            if all(p[i] == patterns[0][i] for p in patterns):
                common_prefix += patterns[0][i]
            else:
                break

        return common_prefix

    def _create_optional_pattern(self, suffix1: str, suffix2: str) -> str:
        """Create optional pattern from two suffixes (e.g., 'g' and 'eg' -> 'e?g')."""
        if not suffix1 or not suffix2:
            return ""

        # Case 1: One suffix is empty, other is single char or short
        if suffix1 == "" and len(suffix2) <= 3:
            return f"{suffix2}?"
        elif suffix2 == "" and len(suffix1) <= 3:
            return f"{suffix1}?"

        # Case 2: One is a single char extension of the other
        if len(suffix1) == len(suffix2) + 1:
            # suffix1 is longer, check if it's suffix2 + one char
            if suffix1.endswith(suffix2):
                missing_char = suffix1[: -len(suffix2)] if suffix2 else suffix1[-1]
                if len(missing_char) == 1:
                    return f"{missing_char}?{suffix2}"
            # Check if suffix1 starts with extra char
            elif suffix1[1:] == suffix2:
                return f"{suffix1[0]}?{suffix2}"
        elif len(suffix2) == len(suffix1) + 1:
            # suffix2 is longer
            if suffix2.endswith(suffix1):
                missing_char = suffix2[: -len(suffix1)] if suffix1 else suffix2[-1]
                if len(missing_char) == 1:
                    return f"{missing_char}?{suffix1}"
            # Check if suffix2 starts with extra char
            elif suffix2[1:] == suffix1:
                return f"{suffix2[0]}?{suffix1}"

        # Case 3: More complex patterns - look for insertions
        if abs(len(suffix1) - len(suffix2)) == 1:
            longer = suffix1 if len(suffix1) > len(suffix2) else suffix2
            shorter = suffix2 if len(suffix1) > len(suffix2) else suffix1

            # Try to find where the extra character is
            for i in range(len(longer)):
                if longer[:i] + longer[i + 1 :] == shorter:
                    # Found the position of the extra character
                    if i == 0:
                        return f"{longer[0]}?{shorter}"
                    elif i == len(longer) - 1:
                        return f"{shorter}{longer[-1]}?"
                    else:
                        return f"{longer[:i]}{longer[i]}?{longer[i + 1 :]}"

        return ""

    def _group_by_common_prefixes(self, patterns: list) -> list:
        """Group patterns by common prefixes for better optimization."""
        if len(patterns) < 2:
            return patterns

        # Group patterns by their prefixes
        prefix_groups = {}

        for pattern in patterns:
            # Try different prefix lengths, but ensure we don't split at invalid positions
            for prefix_len in range(min(len(pattern), 50), 2, -1):
                prefix = pattern[:prefix_len]

                # Check if this is a valid split point (don't split inside character classes or groups)
                if not self._is_valid_split_point(pattern, prefix_len):
                    continue

                # Count how many patterns share this prefix
                matching_patterns = [p for p in patterns if p.startswith(prefix)]

                if len(matching_patterns) >= 2:
                    # Verify that all suffixes would be valid
                    suffixes = [p[len(prefix) :] for p in matching_patterns]
                    if all(self._is_valid_suffix(suffix) for suffix in suffixes):
                        # Found a good grouping
                        if prefix not in prefix_groups:
                            prefix_groups[prefix] = matching_patterns
                        break

        # Apply groupings
        optimized_patterns = []
        used_patterns = set()

        for prefix, group_patterns in prefix_groups.items():
            if len(group_patterns) >= 2 and not any(
                p in used_patterns for p in group_patterns
            ):
                # Extract suffixes
                suffixes = [p[len(prefix) :] for p in group_patterns]

                # Recursively optimize the suffixes (avoid character class optimization to prevent corruption)
                optimized_suffixes = self._optimize_alternation_no_char_class(suffixes)

                # Create the grouped pattern
                if optimized_suffixes.startswith("(?:") and optimized_suffixes.endswith(
                    ")"
                ):
                    # Already properly formatted
                    grouped_pattern = prefix + optimized_suffixes
                elif "|" in optimized_suffixes:
                    # Multiple options, wrap in non-capturing group
                    grouped_pattern = f"{prefix}(?:{optimized_suffixes})"
                else:
                    # Single option
                    grouped_pattern = prefix + optimized_suffixes

                optimized_patterns.append(grouped_pattern)
                used_patterns.update(group_patterns)

        # Add remaining patterns that weren't grouped
        for pattern in patterns:
            if pattern not in used_patterns:
                optimized_patterns.append(pattern)

        return (
            optimized_patterns if len(optimized_patterns) < len(patterns) else patterns
        )

    def _is_valid_split_point(self, pattern: str, split_pos: int) -> bool:
        """Check if splitting a pattern at the given position would be valid."""
        if split_pos <= 0 or split_pos >= len(pattern):
            return False

        # Don't split inside character classes
        in_char_class = False
        escaped = False

        for i in range(split_pos):
            char = pattern[i]

            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
                continue

            if char == "[" and not in_char_class:
                in_char_class = True
            elif char == "]" and in_char_class:
                in_char_class = False

        # If we're inside a character class at the split point, it's invalid
        if in_char_class:
            return False

        # Don't split inside quantifiers like {8} or groups like (?:...)
        if split_pos > 0:
            prev_char = pattern[split_pos - 1]
            if prev_char in "{(":
                return False

        if split_pos < len(pattern):
            next_char = pattern[split_pos]
            if next_char in "}),":
                return False

        return True

    def _is_valid_suffix(self, suffix: str) -> bool:
        """Check if a suffix would be a valid regex fragment."""
        if not suffix:
            return True

        # Suffix shouldn't start with characters that need a prefix
        invalid_starts = ["}", ")", "]", "+", "*", "?", "|"]
        if suffix[0] in invalid_starts:
            return False

        # Check for unbalanced brackets/braces/parens
        brackets = 0
        braces = 0
        parens = 0
        escaped = False

        for char in suffix:
            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
                continue

            if char == "[":
                brackets += 1
            elif char == "]":
                brackets -= 1
            elif char == "{":
                braces += 1
            elif char == "}":
                braces -= 1
            elif char == "(":
                parens += 1
            elif char == ")":
                parens -= 1

            # If any go negative, we have unbalanced
            if brackets < 0 or braces < 0 or parens < 0:
                return False

        return True

    def _is_simple_pattern(self, pattern: str) -> bool:
        """Check if a pattern is simple enough for further optimization."""
        # Patterns with these constructs should not be recursively optimized
        complex_constructs = [
            "(?:",
            "(?=",
            "(?!",
            "(?<=",
            "(?<!",
            "{",
            "}",
            "+",
            "*",
            "?",
        ]
        return not any(construct in pattern for construct in complex_constructs)

    def _optimize_nested_alternations(self, patterns: list) -> list:
        """Extract and optimize common structures from complex patterns."""
        if len(patterns) < 2:
            return patterns

        # Try grouping by common prefixes first
        grouped_result = self._group_by_common_prefixes(patterns)
        if len(grouped_result) < len(patterns):
            return grouped_result

        # Look for patterns that have the same structure but different inner alternations
        # This is a simplified version - could be expanded for more complex cases
        return patterns

    def _optimize_common_parts(self, patterns: list) -> str:
        """Extract common prefixes and suffixes from patterns."""
        if len(patterns) < 2:
            return patterns[0] if patterns else ""

        # Find common prefix
        common_prefix = ""
        if patterns:
            min_len = min(len(p) for p in patterns)
            for i in range(min_len):
                if all(p[i] == patterns[0][i] for p in patterns):
                    common_prefix += patterns[0][i]
                else:
                    break

        # Find common suffix from the remaining parts after removing prefix
        remaining_after_prefix = [p[len(common_prefix) :] for p in patterns]
        common_suffix = ""

        if remaining_after_prefix and all(remaining_after_prefix):
            min_len = min(len(p) for p in remaining_after_prefix)
            for i in range(1, min_len + 1):
                # Check from the end
                if all(
                    p[-i] == remaining_after_prefix[0][-i]
                    for p in remaining_after_prefix
                ):
                    common_suffix = remaining_after_prefix[0][-i] + common_suffix
                else:
                    break

        # Extract middle parts (what's left after removing common prefix and suffix)
        middle_parts = []
        for pattern in patterns:
            start_idx = len(common_prefix)
            end_idx = (
                len(pattern) - len(common_suffix) if common_suffix else len(pattern)
            )

            if start_idx <= end_idx:
                middle_part = pattern[start_idx:end_idx]
                middle_parts.append(middle_part)
            else:
                # Invalid case - suffix and prefix overlap, return original
                return f"(?:{'|'.join(patterns)})"

        # Check if optimization is worthwhile
        # We need either a meaningful common prefix/suffix or significant reduction in unique middle parts
        total_common_len = len(common_prefix) + len(common_suffix)
        unique_middles = list(dict.fromkeys(middle_parts))

        # Calculate potential savings
        original_length = (
            sum(len(p) for p in patterns) + len(patterns) - 1
        )  # account for | separators

        if total_common_len >= 3 or len(unique_middles) < len(patterns):
            # We have optimization potential

            if len(unique_middles) == 1 and unique_middles[0] == "":
                # All patterns are identical after removing common parts
                return common_prefix + common_suffix

            # Filter out empty strings for the alternation, but keep track if we had any
            non_empty_middles = [m for m in unique_middles if m != ""]
            has_empty = "" in unique_middles

            if not non_empty_middles:
                # Only empty middle parts
                return common_prefix + common_suffix
            elif len(non_empty_middles) == 1 and not has_empty:
                # Only one unique non-empty middle part
                return common_prefix + non_empty_middles[0] + common_suffix
            else:
                # Multiple middle parts - create alternation
                if has_empty:
                    # Include empty alternative by making the whole middle part optional
                    if len(non_empty_middles) == 1:
                        middle_alternation = f"(?:{non_empty_middles[0]})?"
                    else:
                        middle_alternation = f"(?:{'|'.join(non_empty_middles)})?"
                else:
                    # No empty parts
                    if len(non_empty_middles) == 1:
                        middle_alternation = non_empty_middles[0]
                    else:
                        middle_alternation = f"(?:{'|'.join(non_empty_middles)})"

                result = common_prefix + middle_alternation + common_suffix

                # Only return optimization if it's actually shorter or significantly reduces repetition
                if (
                    len(result) < original_length * 0.8
                    or len(unique_middles) <= len(patterns) * 0.6
                ):
                    return result

        # No significant optimization found
        return f"(?:{'|'.join(patterns)})"

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
