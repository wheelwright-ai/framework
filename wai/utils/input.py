"""Safe, cross-platform input handling for CLI."""

import sys
import os
import platform
from typing import Optional, List, Tuple, Any


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
