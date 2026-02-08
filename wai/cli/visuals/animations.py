"""
Animation utilities for CLI.
"""

import sys
from .wheel import WagonWheel, get_wagon_wheel


def show_welcome_banner(with_animation: bool = True):
    """Show Wheelwright welcome banner with optional animation.
    
    Args:
        with_animation: Whether to show wagon wheel animation
    """
    # ASCII-compatible banner (Windows-safe)
    if sys.platform == 'win32':
        banner = """
    +===============================================+
    |                                               |
    |         WHEELWRIGHT AI                        |
    |                                               |
    |             v3.2.0                            |
    |                                               |
    |   Build AI wheels that roll                   |
    |   forward forever                             |
    |                                               |
    +===============================================+
    """
    else:
        banner = """
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║       WHEELWRIGHT AI                  ║
    ║                                       ║
    ║           v3.2.0                      ║
    ║                                       ║
    ║   Build AI wheels that roll           ║
    ║   forward forever                     ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
    """
    
    print(banner)
    
    if with_animation:
        wheel = get_wagon_wheel()
        wheel.roll(duration_ms=3000)
