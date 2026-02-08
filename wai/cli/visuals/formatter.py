"""
Rich formatting utilities for CLI output.

Handles tables, colors, and formatted output for all CLI commands.
"""

import sys
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


# Force UTF-8 on Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


@dataclass
class TableColumn:
    """Definition of a table column."""
    name: str
    key: str
    width: Optional[int] = None
    align: str = "left"  # left, center, right


class CLIFormatter:
    """Wrapper for Rich formatting with fallbacks."""
    
    def __init__(self, use_rich: bool = True):
        """Initialize formatter.
        
        Args:
            use_rich: Whether to use Rich library
        """
        self.use_rich = use_rich
        self._init_rich()
    
    def _init_rich(self):
        """Initialize Rich if available."""
        try:
            from rich.console import Console
            from rich.table import Table
            self.console = Console(force_terminal=True, legacy_windows=False)
            self.has_rich = True
        except ImportError:
            self.console = None
            self.has_rich = False
    
    def print_header(self, title: str, width: int = 60):
        """Print a formatted header.
        
        Args:
            title: Header text
            width: Header width
        """
        if self.has_rich and self.use_rich:
            self.console.rule(title, style="bold cyan")
        else:
            # Fallback: simple ASCII header
            print(f"\n{'=' * width}")
            print(f"  {title}")
            print(f"{'=' * width}\n")
    
    def print_success(self, message: str):
        """Print success message.
        
        Args:
            message: Success message
        """
        if self.has_rich and self.use_rich:
            self.console.print(f"[green bold]✓ {message}[/green bold]")
        else:
            print(f"[OK] {message}")
    
    def print_error(self, message: str):
        """Print error message.
        
        Args:
            message: Error message
        """
        if self.has_rich and self.use_rich:
            self.console.print(f"[red bold]✗ {message}[/red bold]")
        else:
            print(f"[ERROR] {message}")
    
    def print_warning(self, message: str):
        """Print warning message.
        
        Args:
            message: Warning message
        """
        if self.has_rich and self.use_rich:
            self.console.print(f"[yellow bold]! {message}[/yellow bold]")
        else:
            print(f"[WARN] {message}")
    
    def print_info(self, message: str):
        """Print info message.
        
        Args:
            message: Info message
        """
        if self.has_rich and self.use_rich:
            self.console.print(f"[cyan]→ {message}[/cyan]")
        else:
            print(f"[INFO] {message}")
    
    def print_table(
        self,
        data: List[Dict[str, Any]],
        columns: Optional[List[TableColumn]] = None,
        title: Optional[str] = None
    ):
        """Print formatted table.
        
        Args:
            data: List of dictionaries
            columns: Column definitions
            title: Optional table title
        """
        if not data:
            self.print_info("No data to display")
            return
        
        if self.has_rich and self.use_rich:
            self._print_rich_table(data, columns, title)
        else:
            self._print_simple_table(data, columns, title)
    
    def _print_rich_table(
        self,
        data: List[Dict[str, Any]],
        columns: Optional[List[TableColumn]] = None,
        title: Optional[str] = None
    ):
        """Print table using Rich library."""
        try:
            from rich.table import Table
            
            table = Table(title=title, style="cyan", show_header=True, header_style="bold cyan")
            
            # Determine columns
            if columns:
                col_keys = [c.key for c in columns]
                col_names = [c.name for c in columns]
            else:
                col_keys = list(data[0].keys()) if data else []
                col_names = col_keys
            
            # Add columns with light color style
            for name in col_names:
                table.add_column(name, style="cyan")
            
            # Add rows
            for row in data:
                values = [str(row.get(key, '')) for key in col_keys]
                table.add_row(*values)
            
            self.console.print(table)
        except Exception:
            # Fallback on error
            self._print_simple_table(data, columns, title)
    
    def _print_simple_table(
        self,
        data: List[Dict[str, Any]],
        columns: Optional[List[TableColumn]] = None,
        title: Optional[str] = None
    ):
        """Print simple ASCII table."""
        if not data:
            return
        
        # Determine columns
        if columns:
            col_keys = [c.key for c in columns]
            col_names = [c.name for c in columns]
        else:
            col_keys = list(data[0].keys())
            col_names = col_keys
        
        # Calculate column widths
        widths = {}
        for key, name in zip(col_keys, col_names):
            max_width = len(name)
            for row in data:
                max_width = max(max_width, len(str(row.get(key, ''))))
            widths[key] = max_width
        
        # Print title
        if title:
            print(f"\n{title}")
            print("=" * sum(widths.values()) + len(widths) * 3)
        
        # Print header
        header = " | ".join(
            name.ljust(widths[key])
            for key, name in zip(col_keys, col_names)
        )
        print(header)
        print("-" * len(header))
        
        # Print rows
        for row in data:
            values = " | ".join(
                str(row.get(key, '')).ljust(widths[key])
                for key in col_keys
            )
            print(values)
        
        print()


# Global formatter instance
_formatter_instance: Optional[CLIFormatter] = None


def get_formatter(use_rich: bool = True) -> CLIFormatter:
    """Get or create formatter instance.
    
    Args:
        use_rich: Whether to use Rich library
    
    Returns:
        CLIFormatter instance
    """
    global _formatter_instance
    if _formatter_instance is None:
        _formatter_instance = CLIFormatter(use_rich=use_rich)
    return _formatter_instance


def reset_formatter():
    """Reset formatter instance (for testing)."""
    global _formatter_instance
    _formatter_instance = None
