"""
Tests for authentication functionality.
"""
import pytest
from src.routes.auth import AuthRouter
from src.services.user_service import UserService
from src.config import AppConfig


class TestAuthRouter:
    """Test authentication routes."""

    def setup_method(self):
        """Set up test fixtures."""
        self.user_service = UserService()
        self.config = AppConfig()
        self.auth_router = AuthRouter(self.user_service, self.config)

    def test_register_success(self):
        """Test successful user registration."""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
        }
        result = self.auth_router.register(data)
        assert result["success"] is True
        assert result["user"]["email"] == "test@example.com"

    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
        }
        # First registration
        self.auth_router.register(data)
        # Second registration with same email
        result = self.auth_router.register(data)
        assert result["success"] is False

    def test_login_success(self):
        """Test successful login."""
        # Register user first
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
        }
        self.auth_router.register(register_data)

        # Login
        result = self.auth_router.login("test@example.com", "SecurePass123!")
        assert result["success"] is True
        assert result["token"] is not None

    def test_login_invalid_password(self):
        """Test login with invalid password."""
        # Register user
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
        }
        self.auth_router.register(register_data)

        # Try login with wrong password
        result = self.auth_router.login("test@example.com", "WrongPassword123!")
        assert result["success"] is False

    def test_verify_token(self):
        """Test token verification."""
        # Register and login
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
        }
        self.auth_router.register(register_data)
        login_result = self.auth_router.login("test@example.com", "SecurePass123!")

        token = login_result["token"]
        verify_result = self.auth_router.verify_token(token)
        assert verify_result["valid"] is True
        assert verify_result["user_id"] is not None
