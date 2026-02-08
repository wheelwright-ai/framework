"""
Menu Formatter - Enhanced CLI menu display with boxes and formatting.

Provides formatted menu output with:
- Box borders
- Color grouping
- Breadcrumb navigation
- Better spacing
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum


class MenuSection(Enum):
    """Menu section types for grouping."""
    PRIMARY = "primary"      # Main commands
    WORKFLOW = "workflow"    # Workflow commands
    UTILITY = "utility"      # Utility commands
    SYSTEM = "system"        # System commands


class MenuFormatter:
    """Format CLI menus with enhanced visual presentation."""
    
    # Box drawing characters (compatible with Windows/Unix)
    BOX_TOP_LEFT = "┌"
    BOX_TOP_RIGHT = "┐"
    BOX_BOTTOM_LEFT = "└"
    BOX_BOTTOM_RIGHT = "┘"
    BOX_HORIZONTAL = "─"
    BOX_VERTICAL = "│"
    BOX_T_RIGHT = "├"
    BOX_T_LEFT = "┤"
    
    # Simplified for compatibility
    SIMPLE_BOXES = {
        "top_left": "+",
        "top_right": "+",
        "bottom_left": "+",
        "bottom_right": "+",
        "horizontal": "-",
        "vertical": "|",
        "t_right": "|",
        "t_left": "|",
    }
    
    # Color codes
    COLORS = {
        "primary": "\033[94m",      # Blue
        "workflow": "\033[92m",     # Green
        "utility": "\033[93m",      # Yellow
        "system": "\033[91m",       # Red
        "reset": "\033[0m",
        "bold": "\033[1m",
    }
    
    def __init__(self, use_colors: bool = True, use_boxes: bool = True, width: int = 80):
        """
        Initialize menu formatter.
        
        Args:
            use_colors: Enable color output
            use_boxes: Enable box borders
            width: Menu width
        """
        self.use_colors = use_colors
        self.use_boxes = use_boxes
        self.width = width

    def _color(self, text: str, section: MenuSection) -> str:
        """Apply color to text if enabled."""
        if not self.use_colors:
            return text
        
        color = self.COLORS.get(section.value, self.COLORS["reset"])
        return f"{color}{text}{self.COLORS['reset']}"

    def _make_box_top(self, title: str = "") -> str:
        """Create top box border."""
        if not self.use_boxes:
            return ""
        
        # Simplified box
        if title:
            padding = max(0, self.width - len(title) - 4)
            return f"┌─{title}─{'─' * padding}┐"
        else:
            return "┌" + "─" * (self.width - 2) + "┐"

    def _make_box_bottom(self) -> str:
        """Create bottom box border."""
        if not self.use_boxes:
            return ""
        return "└" + "─" * (self.width - 2) + "┘"

    def _make_box_line(self, text: str, padding_left: int = 1) -> str:
        """Create boxed line."""
        if not self.use_boxes:
            return text
        
        padding = " " * padding_left
        text_width = self.width - 4
        if len(text) > text_width:
            text = text[:text_width-3] + "..."
        
        remaining = text_width - len(text)
        return f"│{padding}{text}{' ' * remaining}{padding}│"

    def format_menu_header(self, title: str) -> str:
        """Format menu header with title."""
        lines = []
        
        if self.use_boxes:
            lines.append(self._make_box_top(title))
        else:
            lines.append(f"\n{self.COLORS['bold']}{title}{self.COLORS['reset']}")
        
        return "\n".join(lines)

    def format_menu_footer(self) -> str:
        """Format menu footer."""
        if self.use_boxes:
            return self._make_box_bottom()
        return ""

    def format_menu_item(self, 
                        shortcut: str, 
                        name: str, 
                        description: str,
                        section: MenuSection = MenuSection.PRIMARY) -> str:
        """
        Format single menu item.
        
        Args:
            shortcut: Keyboard shortcut (e.g., "1", "i", "init")
            name: Command name
            description: Command description
            section: Menu section for color
        
        Returns:
            Formatted menu line
        """
        # Build the item line
        colored_shortcut = self._color(f"[{shortcut}]", section)
        item = f"{colored_shortcut} {name:<12} → {description}"
        
        # Add box if enabled
        if self.use_boxes:
            return self._make_box_line(item)
        return item

    def format_section(self, 
                      title: str,
                      items: List[Tuple[str, str, str]],
                      section_type: MenuSection = MenuSection.PRIMARY) -> str:
        """
        Format menu section with multiple items.
        
        Args:
            title: Section title
            items: List of (shortcut, name, description) tuples
            section_type: Section type for color
        
        Returns:
            Formatted section
        """
        lines = []
        
        # Section header
        if self.use_boxes:
            header = f"─ {title} "
            padding = self.width - len(header) - 4
            lines.append(f"├─{header}{'─' * max(0, padding)}┤")
        else:
            lines.append(f"\n{self.COLORS['bold']}{title}:{self.COLORS['reset']}")
        
        # Items
        for shortcut, name, description in items:
            lines.append(self.format_menu_item(shortcut, name, description, section_type))
        
        return "\n".join(lines)

    def format_menu(self, sections: Dict[MenuSection, List[Tuple[str, str, str]]]) -> str:
        """
        Format complete menu with multiple sections.
        
        Args:
            sections: Dict of section_type -> list of items
        
        Returns:
            Formatted menu
        """
        lines = []
        
        # Header
        lines.append(self.format_menu_header("Wheelwright CLI Menu"))
        lines.append("")
        
        # Sections in order
        section_order = [
            (MenuSection.PRIMARY, "PRIMARY COMMANDS"),
            (MenuSection.WORKFLOW, "WORKFLOW COMMANDS"),
            (MenuSection.UTILITY, "UTILITY COMMANDS"),
            (MenuSection.SYSTEM, "SYSTEM COMMANDS"),
        ]
        
        for section_type, section_title in section_order:
            if section_type in sections:
                lines.append(self.format_section(
                    section_title,
                    sections[section_type],
                    section_type
                ))
                lines.append("")
        
        # Footer
        lines.append(self.format_menu_footer())
        lines.append("")
        
        return "\n".join(lines)

    def format_breadcrumb(self, path: List[str]) -> str:
        """
        Format breadcrumb navigation.
        
        Args:
            path: List of breadcrumb items
        
        Returns:
            Formatted breadcrumb
        """
        breadcrumb = " > ".join(path)
        if self.use_colors:
            breadcrumb = self._color(breadcrumb, MenuSection.UTILITY)
        return f"📍 {breadcrumb}"

    def format_success(self, message: str) -> str:
        """Format success message."""
        if self.use_colors:
            return f"{self.COLORS['reset']}✅ {message}{self.COLORS['reset']}"
        return f"✓ {message}"

    def format_error(self, message: str) -> str:
        """Format error message."""
        if self.use_colors:
            return f"{self.COLORS['reset']}❌ {message}{self.COLORS['reset']}"
        return f"✗ {message}"

    def format_warning(self, message: str) -> str:
        """Format warning message."""
        if self.use_colors:
            return f"{self.COLORS['reset']}⚠️  {message}{self.COLORS['reset']}"
        return f"⚠ {message}"


def create_formatter(use_colors: bool = True, use_boxes: bool = True) -> MenuFormatter:
    """Create menu formatter with default settings."""
    return MenuFormatter(use_colors=use_colors, use_boxes=use_boxes)


# Example usage
def example_menu():
    """Example of formatted menu output."""
    formatter = create_formatter()
    
    sections = {
        MenuSection.PRIMARY: [
            ("i", "init", "Initialize wheel or hub"),
            ("s", "sync", "Sync with hub"),
            ("c", "closeout", "Close out work cycle"),
        ],
        MenuSection.WORKFLOW: [
            ("t", "teach", "Share teachings with hub"),
            ("l", "learn", "Learn from hub"),
        ],
        MenuSection.UTILITY: [
            ("status", "status", "Check wheel status"),
            ("time", "time", "Check token usage"),
        ],
    }
    
    menu = formatter.format_menu(sections)
    print(menu)
    
    # Show breadcrumb
    print(formatter.format_breadcrumb(["Main Menu", "Workflow"]))
    print()
    
    # Show messages
    print(formatter.format_success("Wheel initialized"))
    print(formatter.format_warning("SSH key not found"))
    print(formatter.format_error("Git push failed"))


if __name__ == "__main__":
    example_menu()
