"""
Safe Input Utilities

Input validation and error handling with KeyboardInterrupt support.
"""

import sys
from typing import Optional, Callable, List

from .exceptions import ValidationError


def safe_input(
    prompt: str,
    default: Optional[str] = None,
    validator: Optional[Callable[[str], bool]] = None,
    max_length: int = 1000,
    allow_empty: bool = False
) -> Optional[str]:
    """
    Safe input with validation and KeyboardInterrupt handling.

    Features:
    - Default value support
    - Custom validator function
    - Length limits
    - Ctrl+C handling (returns None or default)
    - Input sanitization

    Args:
        prompt: Input prompt to display
        default: Default value if user presses Enter
        validator: Optional validation function (returns True if valid)
        max_length: Maximum input length
        allow_empty: Allow empty input

    Returns:
        User input string, default, or None if cancelled

    Examples:
        >>> safe_input("Enter name: ", default="John")
        'John'  # If user presses Enter

        >>> safe_input("Enter email: ", validator=lambda x: '@' in x)
        # Loops until valid email entered
    """
    # Build prompt with default hint
    display_prompt = prompt
    if default is not None:
        display_prompt = f"{prompt} [{default}]: "
    elif not display_prompt.endswith(': '):
        display_prompt = f"{prompt}: "

    while True:
        try:
            user_input = input(display_prompt).strip()

            # Handle empty input
            if not user_input:
                if default is not None:
                    return default
                if allow_empty:
                    return ""
                if not allow_empty:
                    print("   Input cannot be empty. Please try again.")
                    continue

            # Check length
            if len(user_input) > max_length:
                print(f"   Input too long (max {max_length} characters). Please try again.")
                continue

            # Run validator
            if validator and not validator(user_input):
                print("   Invalid input. Please try again.")
                continue

            return user_input

        except KeyboardInterrupt:
            print()  # New line after ^C
            return default if default is not None else None
        except EOFError:
            return default if default is not None else None


def safe_confirm(
    prompt: str,
    default: Optional[bool] = None
) -> bool:
    """
    Yes/no confirmation with error handling.

    Accepts: y, yes, n, no (case insensitive)

    Args:
        prompt: Confirmation prompt
        default: Default response if user presses Enter

    Returns:
        True for yes, False for no

    Examples:
        >>> safe_confirm("Continue?", default=True)
        True  # If user presses Enter

        >>> safe_confirm("Delete file?")
        # Requires explicit y/n
    """
    # Build prompt with default hint
    if default is True:
        hint = " [Y/n]"
    elif default is False:
        hint = " [y/N]"
    else:
        hint = " [y/n]"

    display_prompt = prompt.rstrip() + hint + ": "

    while True:
        try:
            response = input(display_prompt).strip().lower()

            if not response:
                if default is not None:
                    return default
                print("   Please answer yes or no.")
                continue

            if response in ('y', 'yes'):
                return True
            elif response in ('n', 'no'):
                return False
            else:
                print("   Please answer yes or no.")
                continue

        except KeyboardInterrupt:
            print()
            return default if default is not None else False
        except EOFError:
            return default if default is not None else False


def safe_choice(
    prompt: str,
    choices: List[str],
    default: Optional[str] = None,
    case_sensitive: bool = False
) -> Optional[str]:
    """
    Multiple choice selection with validation.

    Args:
        prompt: Selection prompt
        choices: List of valid choices
        default: Default choice if user presses Enter
        case_sensitive: Whether choices are case-sensitive

    Returns:
        Selected choice or None if cancelled

    Examples:
        >>> safe_choice("Select mode:", ["hub", "spoke"], default="spoke")
        'spoke'  # If user presses Enter
    """
    # Prepare choices for comparison
    if not case_sensitive:
        choices_lower = [c.lower() for c in choices]
    else:
        choices_lower = choices

    # Build prompt with choices
    choices_str = '/'.join(choices)
    display_prompt = f"{prompt} ({choices_str})"

    if default:
        display_prompt += f" [{default}]"

    display_prompt += ": "

    while True:
        try:
            response = input(display_prompt).strip()

            if not response:
                if default is not None:
                    return default
                print(f"   Please choose one of: {choices_str}")
                continue

            # Check if response is valid
            check_response = response.lower() if not case_sensitive else response

            if check_response in choices_lower:
                # Return the original cased version
                idx = choices_lower.index(check_response)
                return choices[idx]
            else:
                print(f"   Invalid choice. Please choose one of: {choices_str}")
                continue

        except KeyboardInterrupt:
            print()
            return default if default is not None else None
        except EOFError:
            return default if default is not None else None


def safe_multiline_input(
    prompt: str,
    end_marker: str = "",
    allow_empty: bool = False
) -> List[str]:
    """
    Multi-line input collection.

    Args:
        prompt: Prompt to display
        end_marker: Line to signal end (empty line by default)
        allow_empty: Allow empty list

    Returns:
        List of input lines (excluding end marker)

    Examples:
        >>> safe_multiline_input("Enter paths (empty line to finish):")
        # User enters:
        # /home/user/project1
        # /home/user/project2
        # <empty line>
        ['/home/user/project1', '/home/user/project2']
    """
    print(prompt)
    lines = []

    try:
        while True:
            line = input("   ").strip()

            if line == end_marker:
                break

            if line:  # Only add non-empty lines
                lines.append(line)

    except KeyboardInterrupt:
        print()
        return lines
    except EOFError:
        return lines

    if not lines and not allow_empty:
        return []

    return lines


def print_error(message: str):
    """Print error message to stderr."""
    print(f"   Error: {message}", file=sys.stderr)


def print_warning(message: str):
    """Print warning message."""
    print(f"   Warning: {message}")


def print_success(message: str):
    """Print success message."""
    print(f"   ✓ {message}")


def print_info(message: str):
    """Print informational message."""
    print(f"   {message}")


def safe_menu_choice(
    prompt: str,
    options: List[tuple],
    default: Optional[str] = None
) -> Optional[str]:
    """
    Menu selection with both number and letter shortcuts.

    Simplified UX: Only shows full option list if user enters invalid input.

    Args:
        prompt: Selection prompt
        options: List of tuples: (number, letter, display_text, return_value)
                 e.g., ('1', 'h', 'Hub', 'hub')
        default: Default choice (number or letter)

    Returns:
        Return value of selected option, or None if cancelled

    Examples:
        >>> options = [
        ...     ('1', 'h', '🏢 Hub', 'hub'),
        ...     ('2', 's', '🎡 Spokes', 'spokes'),
        ...     ('q', 'q', '👋 Quit', 'quit')
        ... ]
        >>> safe_menu_choice("Select", options, default='2')
        # First prompt: "Select [2]: "
        # If invalid: "Invalid. Choose: 1/h/2/s/q"
    """
    # Build valid inputs mapping
    valid_inputs = {}
    for num, letter, display, return_val in options:
        if num:
            valid_inputs[num.lower()] = return_val
        if letter:
            valid_inputs[letter.lower()] = return_val

    # Build choices string (only shown on error)
    choices = []
    for num, letter, display, return_val in options:
        if num and letter and num != letter:
            choices.append(f"{num}/{letter}")
        elif num:
            choices.append(num)
        else:
            choices.append(letter)

    choices_str = '/'.join(choices)

    # Simplified prompt
    display_prompt = f"\n{prompt}"

    if default:
        display_prompt += f" [{default}]"

    display_prompt += ": "

    first_try = True

    while True:
        try:
            response = input(display_prompt).strip().lower()

            if not response:
                if default is not None:
                    if default.lower() in valid_inputs:
                        return valid_inputs[default.lower()]
                # Only show options on subsequent tries
                if first_try:
                    print(f"   Please enter a selection.")
                    first_try = False
                else:
                    print(f"   Choose: {choices_str}")
                continue

            if response in valid_inputs:
                return valid_inputs[response]
            else:
                # Show full options list on invalid input
                print(f"   Invalid. Choose: {choices_str}")
                first_try = False
                continue

        except KeyboardInterrupt:
            print()
            return None
        except EOFError:
            return None
