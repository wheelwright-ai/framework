"""
Tests for user service.
"""
import pytest
from src.services.user_service import UserService
from src.models import UserRole


class TestUserService:
    """Test user service operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = UserService()

    def test_create_user_success(self):
        """Test successful user creation."""
        result = self.service.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="SecurePass123!",
        )
        assert result["success"] is True
        assert result["user"].email == "test@example.com"

    def test_create_user_invalid_email(self):
        """Test user creation with invalid email."""
        result = self.service.create_user(
            email="invalid-email",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="SecurePass123!",
        )
        assert result["success"] is False
        assert "email" in str(result["errors"]).lower()

    def test_create_user_weak_password(self):
        """Test user creation with weak password."""
        result = self.service.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="weak",
        )
        assert result["success"] is False

    def test_get_user_by_email(self):
        """Test getting user by email."""
        # Create user
        self.service.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="SecurePass123!",
        )

        # Get user
        user = self.service.get_user_by_email("test@example.com")
        assert user is not None
        assert user.email == "test@example.com"

    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        # Create user
        self.service.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="SecurePass123!",
        )

        # Authenticate
        result = self.service.authenticate_user("test@example.com", "SecurePass123!")
        assert result["authenticated"] is True

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password."""
        # Create user
        self.service.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="SecurePass123!",
        )

        # Authenticate with wrong password
        result = self.service.authenticate_user("test@example.com", "WrongPass123!")
        assert result["authenticated"] is False

    def test_update_user(self):
        """Test updating user information."""
        # Create user
        create_result = self.service.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="SecurePass123!",
        )
        user_id = create_result["user"].id

        # Update user
        updated = self.service.update_user(user_id, first_name="Updated")
        assert updated.first_name == "Updated"
