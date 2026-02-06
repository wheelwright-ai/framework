"""
Tests for validation utilities.
"""
import pytest
from src.utils.validation import Validator


class TestValidator:
    """Test validation utilities."""

    def test_validate_email_valid(self):
        """Test email validation with valid email."""
        assert Validator.validate_email("test@example.com") is True
        assert Validator.validate_email("user.name@domain.co.uk") is True

    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        assert Validator.validate_email("invalid") is False
        assert Validator.validate_email("@example.com") is False
        assert Validator.validate_email("user@") is False

    def test_validate_phone_valid(self):
        """Test phone validation with valid numbers."""
        assert Validator.validate_phone("1234567890") is True
        assert Validator.validate_phone("+11234567890") is True

    def test_validate_phone_invalid(self):
        """Test phone validation with invalid numbers."""
        assert Validator.validate_phone("123") is False
        assert Validator.validate_phone("") is False

    def test_validate_slug_valid(self):
        """Test slug validation with valid slugs."""
        assert Validator.validate_slug("valid-slug") is True
        assert Validator.validate_slug("product-name-123") is True

    def test_validate_slug_invalid(self):
        """Test slug validation with invalid slugs."""
        assert Validator.validate_slug("Invalid Slug") is False
        assert Validator.validate_slug("slug_with_underscore") is False

    def test_validate_password_strength_strong(self):
        """Test password strength validation with strong password."""
        result = Validator.validate_password_strength("SecurePass123!")
        assert result["is_strong"] is True
        assert len(result["messages"]) == 0

    def test_validate_password_strength_weak(self):
        """Test password strength validation with weak password."""
        result = Validator.validate_password_strength("weak")
        assert result["is_strong"] is False
        assert len(result["messages"]) > 0

    def test_validate_required_fields_valid(self):
        """Test required fields validation with all fields."""
        data = {"name": "John", "email": "john@example.com"}
        result = Validator.validate_required_fields(data, ["name", "email"])
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_required_fields_missing(self):
        """Test required fields validation with missing fields."""
        data = {"name": "John"}
        result = Validator.validate_required_fields(data, ["name", "email"])
        assert result["valid"] is False
        assert "email" in result["errors"]
