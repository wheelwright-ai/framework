"""Safe, cross-platform input handling for CLI."""

import sys
import os
import platform
from typing import Optional, List, Tuple, Any


# Import formatter functions for compatibility
def _get_formatter():
    """Lazy import formatter to avoid circular dependencies."""
    try:
        from ..cli.visuals.formatter import get_formatter
        return get_formatter()
    except ModuleNotFoundError:
        # Fallback for when CLI components are not available (e.g., during testing or standalone script execution)
        class DummyFormatter:
            def info(self, msg): print(msg)
            def success(self, msg): print(msg)
            def error(self, msg): print(f"ERROR: {msg}")
            def warning(self, msg): print(f"WARNING: {msg}")
            def print_info(self, msg): print(msg) # Added for compatibility with existing calls
            def print_success(self, msg): print(msg)
            def print_error(self, msg): print(f"ERROR: {msg}")
            def print_warning(self, msg): print(f"WARNING: {msg}")
        return DummyFormatter()


def print_info(message: str):
    """Print info message."""
    formatter = _get_formatter()
    return formatter.print_info(message)


def print_success(message: str):
    """Print success message."""
    formatter = _get_formatter()
    return formatter.print_success(message)


def print_error(message: str):
    """Print error message."""
    formatter = _get_formatter()
    return formatter.print_error(message)


def print_warning(message: str):
    """Print warning message."""
    formatter = _get_formatter()
    return formatter.print_warning(message)


def safe_confirm(prompt: str = "Proceed?", default: bool = False) -> bool:
    """Get yes/no confirmation from user.
    
    Args:
        prompt: Confirmation prompt
        default: Default value if empty
    
    Returns:
        True for yes, False for no
    """
    try:
        default_str = "y" if default else "n"
        response = safe_input(f"{prompt} ({default_str}): ", default_str)
        return response.lower().startswith('y')
    except (KeyboardInterrupt, EOFError):
        return False
    except Exception:
        return default


def safe_choice(prompt: str, choices: List[str], default: int = 0) -> Optional[str]:
    """Get choice from list.
    
    Args:
        prompt: Choice prompt
        choices: List of options
        default: Default index
    
    Returns:
        Selected choice or None
    """
    try:
        print_info(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            print_info(f"  {i}. {choice}")
        response = safe_input(f"Select [1-{len(choices)}]: ", str(default + 1))
        idx = int(response) - 1
        return choices[idx] if 0 <= idx < len(choices) else choices[default]
    except (ValueError, IndexError, KeyboardInterrupt):
        return choices[default]
    except Exception:
        return None


def single_key_input() -> Optional[str]:
    """Get single key input."""
    return safe_getch()


def safe_input(prompt: str = "", default: str = "") -> str:
    """Get user input safely with encoding handling.
    
    Args:
        prompt: Text to display
        default: Default value if empty
    
    Returns:
        User input or default
    """
    try:
        # Ensure encoding on Windows
        if sys.platform == 'win32':
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            if hasattr(sys.stdin, 'reconfigure'):
                sys.stdin.reconfigure(encoding='utf-8', errors='replace')
        
        result = input(prompt)
        return result if result else default
    except EOFError:
        return default
    except UnicodeDecodeError:
        # Fall back to safe input
        return default
    except KeyboardInterrupt:
        raise
    except Exception:
        return default


def safe_menu_choice(
    prompt: str,
    options: List[Tuple[str, str, str, Any]],
    default: str = "1"
) -> Any:
    """Display menu and get selection safely.
    
    Args:
        prompt: Menu prompt
        options: List of (number, letter, display, value)
        default: Default selection
    
    Returns:
        Selected value
    """
    try:
        choice = safe_input(f"\n{prompt} [{default}]: ", default)
        
        # Find matching option
        for num, letter, display, value in options:
            if choice == num or choice == letter or choice.lower() == letter:
                return value
        
        # Not found, return default
        for num, letter, display, value in options:
            if num == default or letter == default:
                return value
        
        # Fallback
        return options[0][3] if options else None
    
    except KeyboardInterrupt:
        return None
    except Exception:
        return None


def safe_getch() -> Optional[str]:
    """Get single character from input (cross-platform).
    
    Returns:
        Single character or None
    """
    try:
        if sys.platform == 'win32':
            import msvcrt
            char = msvcrt.getch()
            return char.decode('utf-8', errors='ignore') if char else None
        else:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                char = sys.stdin.read(1)
                return char if char else None
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except ImportError:
        # Fallback for systems without tty
        return safe_input("")
    except Exception:
        return None
