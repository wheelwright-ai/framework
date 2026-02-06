"""Tests for DataFormatter."""
import pytest
from src.formatters import DataFormatter

def test_format_name():
    """Test name formatting."""
    formatter = DataFormatter()
    result = formatter.format({'name': '  john doe  '})
    assert result['name'] == 'John Doe'

def test_format_email():
    """Test email formatting."""
    formatter = DataFormatter()
    result = formatter.format({'email': '  TEST@EXAMPLE.COM  '})
    assert result['email'] == 'test@example.com'

def test_strict_mode():
    """Test strict mode validation."""
    formatter = DataFormatter({'strict': True})
    with pytest.raises(ValueError):
        formatter.format({'email': 'invalid'})
