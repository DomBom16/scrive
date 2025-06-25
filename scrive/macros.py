import re
from typing import Union

from .standalone import char_range, digit, exactly
from .core import Scrive


def choice(*patterns: Union[Scrive, str]) -> Scrive:
    """Create alternation (OR) of patterns."""
    if not patterns:
        raise ValueError(
            "choice() requires at least one pattern. Provide strings or Scrive patterns to choose from."
        )

    if len(patterns) == 1:
        pattern = patterns[0]
        return pattern if isinstance(pattern, Scrive) else exactly(str(pattern))

    # Collect all pattern strings
    pattern_strs = []
    flags = 0

    for pattern in patterns:
        if isinstance(pattern, Scrive):
            pattern_strs.append(pattern.pattern)
            flags |= pattern.flags
        else:
            pattern_strs.append(re.escape(str(pattern)))

    # Use automatic optimization
    dummy_scrive = Scrive("", flags)
    combined = dummy_scrive._optimize_alternation(pattern_strs)
    return Scrive(combined, flags)


def create(*patterns: Union[Scrive, str], flags: int = 0) -> Scrive:
    """Create a Scrive object from patterns."""
    if not patterns:
        return Scrive("", flags)

    # Combine all patterns
    combined = Scrive("", flags)
    for pattern in patterns:
        if isinstance(pattern, Scrive):
            combined = combined + pattern
        else:
            combined = combined + exactly(str(pattern))

    return combined


def separated_by(
    element: Union[Scrive, str], separator: Union[Scrive, str], count: int
) -> Scrive:
    """Create pattern with element repeated 'count' times, separated by 'separator'.

    Example: separated_by(digit(), exactly("."), 4) creates "(?:digit\\.){3}digit"

    Args:
        element: The element pattern to repeat
        separator: The separator pattern between elements
        count: Number of times to repeat the element (must be >= 1)

    Returns:
        New Scrive object with the alternating pattern
    """
    if count < 1:
        raise ValueError("count must be at least 1")

    # Convert to Scrive objects if needed
    if not isinstance(element, Scrive):
        element = exactly(str(element))
    if not isinstance(separator, Scrive):
        separator = exactly(str(separator))

    if count == 1:
        return Scrive(element.pattern)

    # Optimize pattern: (element + separator){count-1} + element
    element_plus_separator = Scrive(
        element.pattern + separator.pattern
    ).non_capturing_group()
    repeated_part = element_plus_separator.times(count - 1)
    final_element = Scrive(element.pattern)

    return repeated_part + final_element


def decimal_range(min_val: int, max_val: int) -> Scrive:
    """Generate regex pattern matching decimal numbers in the given range.

    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)

    Returns:
        Scrive pattern that matches numbers in the range

    Example:
        decimal_range(0, 255) generates pattern for IPv4 octets
        decimal_range(1, 12) generates pattern for months
    """
    if min_val > max_val:
        raise ValueError("min_val cannot be greater than max_val")
    if min_val < 0 or max_val < 0:
        raise ValueError("negative numbers not supported")

    # Get the number of digits in min and max values
    min_digits = len(str(min_val))
    max_digits = len(str(max_val))

    patterns = []

    # Generate patterns for each possible digit count
    for digit_count in range(min_digits, max_digits + 1):
        # Calculate the range for this digit count
        range_min = max(min_val, 10 ** (digit_count - 1) if digit_count > 1 else 0)
        range_max = min(max_val, 10**digit_count - 1)

        if range_min <= range_max:
            pattern = _generate_numeric_range(range_min, range_max)
            if pattern:
                patterns.append(pattern)

    if len(patterns) == 1:
        return patterns[0]
    else:
        return choice(*patterns)


def _generate_numeric_range(min_val: int, max_val: int) -> Scrive | None:
    """Generate pattern for numeric range using recursive digit-by-digit approach."""
    if min_val == max_val:
        return exactly(str(min_val))

    if min_val > max_val:
        return None

    # Convert to strings to work with digits
    min_str = str(min_val)
    max_str = str(max_val)

    # Pad to same length
    max_len = max(len(min_str), len(max_str))
    min_str = min_str.zfill(max_len)
    max_str = max_str.zfill(max_len)

    pattern = _generate_digit_by_digit(min_str, max_str, 0)
    return _optimize_digit_patterns(pattern) if pattern else None


def _generate_digit_by_digit(
    min_str: str, max_str: str, position: int
) -> Scrive | None:
    """Recursively generate pattern digit by digit."""
    if position >= len(min_str):
        return None

    min_digit = int(min_str[position])
    max_digit = int(max_str[position])

    patterns = []

    # Handle each possible digit value at this position
    for digit_val in range(min_digit, max_digit + 1):
        if position == len(min_str) - 1:
            # Last digit - create character range or exact match
            if min_digit == max_digit:
                patterns.append(exactly(str(digit_val)))
            else:
                # We'll handle this as a range after the loop
                pass
        else:
            # Not the last digit - need to recurse
            if digit_val == min_digit and digit_val == max_digit:
                # Same digit in both bounds - recurse with same constraints
                sub_pattern = _generate_digit_by_digit(min_str, max_str, position + 1)
                if sub_pattern:
                    patterns.append(exactly(str(digit_val)) + sub_pattern)
            elif digit_val == min_digit:
                # First digit - constrain by minimum for remaining digits
                remaining_min = min_str[position + 1 :]
                remaining_max = "9" * (len(min_str) - position - 1)
                sub_pattern = _generate_digit_by_digit(remaining_min, remaining_max, 0)
                if sub_pattern:
                    patterns.append(exactly(str(digit_val)) + sub_pattern)
            elif digit_val == max_digit:
                # Last digit - constrain by maximum for remaining digits
                remaining_min = "0" * (len(min_str) - position - 1)
                remaining_max = max_str[position + 1 :]
                sub_pattern = _generate_digit_by_digit(remaining_min, remaining_max, 0)
                if sub_pattern:
                    patterns.append(exactly(str(digit_val)) + sub_pattern)
            else:
                # Middle digit - any remaining digits allowed
                remaining_pattern = digit()
                for _ in range(len(min_str) - position - 2):
                    remaining_pattern = remaining_pattern + digit()
                patterns.append(exactly(str(digit_val)) + remaining_pattern)

    # Handle range at final position
    if position == len(min_str) - 1 and min_digit != max_digit:
        if min_digit == 0 and max_digit == 9:
            patterns = [digit()]
        else:
            patterns = [char_range(str(min_digit), str(max_digit))]

    if len(patterns) == 0:
        return None
    elif len(patterns) == 1:
        return patterns[0]
    else:
        result = choice(*patterns)
        return _optimize_digit_patterns(result)


def _optimize_digit_patterns(pattern: Scrive) -> Scrive:
    """Algorithmically optimize repetitive digit patterns."""
    if not pattern:
        return pattern

    pattern_str = pattern.pattern

    # Extract and optimize choice patterns recursively
    optimized_str = _optimize_choice_pattern(pattern_str)

    return Scrive(optimized_str)


def _optimize_choice_pattern(pattern_str: str) -> str:
    """Recursively optimize choice patterns."""
    import re

    # Find choice patterns (?:...|...|...)
    choice_pattern = re.compile(r"\(\?\:([^)]+)\)")

    def optimize_match(match):
        content = match.group(1)
        alternatives = content.split("|")

        # Optimize digit+\d patterns
        optimized_alternatives = _optimize_digit_d_patterns(alternatives)
        # optimized_alternatives = alternatives

        # Recursively optimize nested patterns
        optimized_alternatives = [
            _optimize_choice_pattern(alt) for alt in optimized_alternatives
        ]

        if len(optimized_alternatives) == 1:
            return optimized_alternatives[0]
        else:
            return f"(?:{'|'.join(optimized_alternatives)})"

    return choice_pattern.sub(optimize_match, pattern_str)


def _optimize_digit_d_patterns(alternatives: list) -> list:
    """Optimize digit+\\d patterns in a list of alternatives."""
    import re

    # Find alternatives that match digit followed by one or more \d
    digit_d_pattern = re.compile(r"^(\d)((?:\\d)+)$")
    pattern_groups = {}  # suffix_pattern -> {digit: original_alternative}
    other_alternatives = []

    for alt in alternatives:
        alt = alt.strip()
        match = digit_d_pattern.match(alt)
        if match:
            digit = int(match.group(1))
            suffix = match.group(2)  # The \d\d\d... part

            if suffix not in pattern_groups:
                pattern_groups[suffix] = {}
            pattern_groups[suffix][digit] = alt
        else:
            other_alternatives.append(alt)

    optimized_groups = []

    # Process each suffix pattern group
    for suffix, digit_alternatives in pattern_groups.items():
        if len(digit_alternatives) < 3:
            # Not worth optimizing, keep individual patterns
            for alt in digit_alternatives.values():
                optimized_groups.append(alt)
            continue

        sorted_digits = sorted(digit_alternatives.keys())
        current_group = [sorted_digits[0]]

        for i in range(1, len(sorted_digits)):
            if sorted_digits[i] == current_group[-1] + 1:
                current_group.append(sorted_digits[i])
            else:
                # End current group, start new one
                if len(current_group) >= 3:
                    # Optimize this group
                    if current_group[0] == 0 and current_group[-1] == 9:
                        optimized_groups.append(f"\\d{suffix}")
                    else:
                        optimized_groups.append(
                            f"[{current_group[0]}-{current_group[-1]}]{suffix}"
                        )
                else:
                    # Keep individual patterns
                    for digit in current_group:
                        optimized_groups.append(digit_alternatives[digit])

                current_group = [sorted_digits[i]]

        # Handle last group
        if len(current_group) >= 3:
            if current_group[0] == 0 and current_group[-1] == 9:
                optimized_groups.append(f"\\d{suffix}")
            else:
                optimized_groups.append(
                    f"[{current_group[0]}-{current_group[-1]}]{suffix}"
                )
        else:
            for digit in current_group:
                optimized_groups.append(digit_alternatives[digit])

    # Add back non-digit alternatives
    return optimized_groups + other_alternatives
