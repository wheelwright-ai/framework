"""
Color scheme for CLI - optimized for dark terminal backgrounds.
"""

import sys


class ColorScheme:
    """Colors optimized for readability on dark backgrounds."""
    
    # ANSI escape codes - using BRIGHT colors for dark backgrounds
    BRIGHT_CYAN = "\033[1;36m"    # Bright cyan
    BRIGHT_GREEN = "\033[1;32m"   # Bright green
    BRIGHT_YELLOW = "\033[1;33m"  # Bright yellow
    BRIGHT_RED = "\033[1;31m"     # Bright red
    BRIGHT_BLUE = "\033[1;34m"    # Bright blue
    BRIGHT_MAGENTA = "\033[1;35m" # Bright magenta
    WHITE = "\033[1;37m"          # Bright white
    
    # Basic colors (non-bright, for contrast)
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    
    # Reset
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Special
    UNDERLINE = "\033[4m"
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return sys.platform == 'win32'
    
    @staticmethod
    def format(text: str, color: str, bold: bool = False) -> str:
        """Format text with color.
        
        Args:
            text: Text to format
            color: Color code
            bold: Whether to make bold
        
        Returns:
            Formatted text
        """
        if bold:
            return f"{ColorScheme.BOLD}{color}{text}{ColorScheme.RESET}"
        return f"{color}{text}{ColorScheme.RESET}"
    
    @staticmethod
    def success(text: str) -> str:
        """Format success message (green)."""
        return ColorScheme.format(f"[OK] {text}", ColorScheme.BRIGHT_GREEN)
    
    @staticmethod
    def error(text: str) -> str:
        """Format error message (red)."""
        return ColorScheme.format(f"[ERROR] {text}", ColorScheme.BRIGHT_RED)
    
    @staticmethod
    def warning(text: str) -> str:
        """Format warning message (yellow)."""
        return ColorScheme.format(f"[WARN] {text}", ColorScheme.BRIGHT_YELLOW)
    
    @staticmethod
    def info(text: str) -> str:
        """Format info message (cyan)."""
        return ColorScheme.format(f"[INFO] {text}", ColorScheme.BRIGHT_CYAN)
    
    @staticmethod
    def header(text: str) -> str:
        """Format header (bright white + bold)."""
        return ColorScheme.format(text, ColorScheme.WHITE, bold=True)
    
    @staticmethod
    def section(text: str) -> str:
        """Format section title (bright cyan + bold)."""
        return ColorScheme.format(text, ColorScheme.BRIGHT_CYAN, bold=True)
