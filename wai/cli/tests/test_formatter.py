"""
Tests for CLI formatter module.

Comprehensive tests for:
- Message formatting (success, error, warning, info)
- Table formatting (Rich and fallback)
- Color output
- Graceful degradation
"""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

from wai.cli.visuals.formatter import CLIFormatter, TableColumn, get_formatter, reset_formatter


class TestCLIFormatterInitialization:
    """Test formatter initialization."""
    
    def test_formatter_initializes(self):
        """Formatter should initialize without errors."""
        formatter = CLIFormatter(use_rich=False)
        assert formatter is not None
    
    def test_formatter_detects_rich(self):
        """Formatter should detect Rich library."""
        formatter = CLIFormatter(use_rich=True)
        # Should attempt to load Rich
        # has_rich will be True or False depending on installation
        assert hasattr(formatter, 'has_rich')
    
    def test_formatter_respects_use_rich_flag(self):
        """Formatter should respect use_rich flag."""
        formatter = CLIFormatter(use_rich=False)
        assert formatter.use_rich is False


class TestMessageFormatting:
    """Test message formatting methods."""
    
    def test_print_success(self, capsys):
        """Should print success message."""
        formatter = CLIFormatter(use_rich=False)
        formatter.print_success("Test message")
        captured = capsys.readouterr()
        assert "✅" in captured.out
        assert "Test message" in captured.out
    
    def test_print_error(self, capsys):
        """Should print error message."""
        formatter = CLIFormatter(use_rich=False)
        formatter.print_error("Error message")
        captured = capsys.readouterr()
        assert "❌" in captured.out
        assert "Error message" in captured.out
    
    def test_print_warning(self, capsys):
        """Should print warning message."""
        formatter = CLIFormatter(use_rich=False)
        formatter.print_warning("Warning message")
        captured = capsys.readouterr()
        assert "⚠️" in captured.out
        assert "Warning message" in captured.out
    
    def test_print_info(self, capsys):
        """Should print info message."""
        formatter = CLIFormatter(use_rich=False)
        formatter.print_info("Info message")
        captured = capsys.readouterr()
        assert "ℹ️" in captured.out
        assert "Info message" in captured.out
    
    def test_print_header(self, capsys):
        """Should print header."""
        formatter = CLIFormatter(use_rich=False)
        formatter.print_header("Test Header")
        captured = capsys.readouterr()
        assert "Test Header" in captured.out


class TestTableFormatting:
    """Test table formatting."""
    
    def test_print_table_with_data(self, capsys):
        """Should print table with data."""
        formatter = CLIFormatter(use_rich=False)
        data = [
            {"name": "Alice", "status": "Active"},
            {"name": "Bob", "status": "Inactive"}
        ]
        formatter.print_table(data)
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "Bob" in captured.out
        assert "name" in captured.out or "Name" in captured.out
    
    def test_print_table_empty_data(self, capsys):
        """Should handle empty data gracefully."""
        formatter = CLIFormatter(use_rich=False)
        formatter.print_table([])
        captured = capsys.readouterr()
        assert "No data" in captured.out
    
    def test_print_table_with_columns(self, capsys):
        """Should use column definitions."""
        formatter = CLIFormatter(use_rich=False)
        columns = [
            TableColumn(name="Project", key="name"),
            TableColumn(name="Status", key="status")
        ]
        data = [
            {"name": "ProjectA", "status": "Active"}
        ]
        formatter.print_table(data, columns=columns, title="Projects")
        captured = capsys.readouterr()
        assert "Project" in captured.out or "ProjectA" in captured.out
    
    def test_print_table_with_title(self, capsys):
        """Should print title with table."""
        formatter = CLIFormatter(use_rich=False)
        data = [{"col1": "val1"}]
        formatter.print_table(data, title="Test Table")
        captured = capsys.readouterr()
        assert "Test Table" in captured.out
    
    def test_print_table_multiple_rows(self, capsys):
        """Should print multiple rows."""
        formatter = CLIFormatter(use_rich=False)
        data = [
            {"id": "1", "name": "Item1"},
            {"id": "2", "name": "Item2"},
            {"id": "3", "name": "Item3"}
        ]
        formatter.print_table(data)
        captured = capsys.readouterr()
        assert "Item1" in captured.out
        assert "Item2" in captured.out
        assert "Item3" in captured.out
    
    def test_simple_table_handles_missing_keys(self, capsys):
        """Should handle rows with missing keys."""
        formatter = CLIFormatter(use_rich=False)
        data = [
            {"name": "Alice", "status": "Active"},
            {"name": "Bob"}  # Missing 'status'
        ]
        formatter.print_table(data)
        captured = capsys.readouterr()
        # Should not crash
        assert "Alice" in captured.out


class TestTableColumn:
    """Test TableColumn dataclass."""
    
    def test_table_column_creation(self):
        """Should create table column."""
        col = TableColumn(name="Name", key="name")
        assert col.name == "Name"
        assert col.key == "name"
    
    def test_table_column_with_width(self):
        """Should accept width."""
        col = TableColumn(name="Name", key="name", width=20)
        assert col.width == 20
    
    def test_table_column_with_alignment(self):
        """Should accept alignment."""
        col = TableColumn(name="Value", key="value", align="right")
        assert col.align == "right"
    
    def test_table_column_defaults(self):
        """Should have reasonable defaults."""
        col = TableColumn(name="Test", key="test")
        assert col.width is None
        assert col.align == "left"


class TestFormatterSingleton:
    """Test singleton pattern."""
    
    def test_get_formatter_returns_instance(self):
        """Should return formatter instance."""
        reset_formatter()
        formatter = get_formatter()
        assert isinstance(formatter, CLIFormatter)
    
    def test_get_formatter_caches(self):
        """Should cache formatter instance."""
        reset_formatter()
        fmt1 = get_formatter()
        fmt2 = get_formatter()
        assert fmt1 is fmt2
    
    def test_reset_formatter(self):
        """Should reset singleton."""
        reset_formatter()
        fmt1 = get_formatter()
        reset_formatter()
        fmt2 = get_formatter()
        assert fmt1 is not fmt2


class TestFormatterGracefulDegradation:
    """Test graceful degradation without Rich."""
    
    def test_works_without_rich(self, capsys):
        """Should work even if Rich is not available."""
        formatter = CLIFormatter(use_rich=False)
        formatter.print_success("Test")
        captured = capsys.readouterr()
        # Should still output something
        assert "Test" in captured.out
    
    def test_table_fallback_works(self, capsys):
        """Should fallback to simple table."""
        formatter = CLIFormatter(use_rich=False)
        data = [{"name": "Test"}]
        formatter.print_table(data)
        captured = capsys.readouterr()
        # Should still display data
        assert "Test" in captured.out


class TestFormatterEdgeCases:
    """Test edge cases."""
    
    def test_print_success_empty_message(self, capsys):
        """Should handle empty messages."""
        formatter = CLIFormatter(use_rich=False)
        formatter.print_success("")
        captured = capsys.readouterr()
        assert "✅" in captured.out
    
    def test_print_table_with_none_values(self, capsys):
        """Should handle None values."""
        formatter = CLIFormatter(use_rich=False)
        data = [
            {"name": "Alice", "status": None}
        ]
        formatter.print_table(data)
        captured = capsys.readouterr()
        assert "Alice" in captured.out
    
    def test_print_table_with_special_characters(self, capsys):
        """Should handle special characters."""
        formatter = CLIFormatter(use_rich=False)
        data = [
            {"name": "Project™", "status": "Active®"}
        ]
        formatter.print_table(data)
        captured = capsys.readouterr()
        assert "Project™" in captured.out
    
    def test_print_header_custom_width(self, capsys):
        """Should respect custom width."""
        formatter = CLIFormatter(use_rich=False)
        formatter.print_header("Test", width=20)
        captured = capsys.readouterr()
        assert "Test" in captured.out


class TestFormatterRichIntegration:
    """Test Rich library integration."""
    
    @patch('wai.cli.visuals.formatter.Console')
    def test_uses_rich_when_available(self, mock_console):
        """Should use Rich when available."""
        formatter = CLIFormatter(use_rich=True)
        # Rich might not be installed, but test the flag
        assert formatter.use_rich is True


class TestFormatterIntegration:
    """Integration tests."""
    
    def test_full_workflow(self, capsys):
        """Test complete workflow."""
        formatter = CLIFormatter(use_rich=False)
        
        # Print header
        formatter.print_header("Test Section")
        
        # Print messages
        formatter.print_info("Starting operation")
        
        # Print table
        data = [
            {"item": "ItemA", "value": "100"},
            {"item": "ItemB", "value": "200"}
        ]
        formatter.print_table(data, title="Results")
        
        # Print results
        formatter.print_success("Operation complete")
        
        captured = capsys.readouterr()
        assert "Test Section" in captured.out
        assert "Starting operation" in captured.out
        assert "ItemA" in captured.out
        assert "Operation complete" in captured.out
    
    def test_multiple_formatters_independent(self):
        """Multiple formatter instances should be independent."""
        fmt1 = CLIFormatter(use_rich=False)
        fmt2 = CLIFormatter(use_rich=True)
        assert fmt1 is not fmt2
        assert fmt1.use_rich is False
        assert fmt2.use_rich is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
