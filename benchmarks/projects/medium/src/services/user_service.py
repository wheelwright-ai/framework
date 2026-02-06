"""
User management service.
Handles user creation, validation, and profile management.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.password import PasswordManager
from src.utils.validation import Validator
from src.models import User, UserRole


logger = get_logger(__name__)


class UserService:
    """Service for user-related operations."""

    def __init__(self):
        self.users_db = {}

    def create_user(
        self,
        email: str,
        username: str,
        first_name: str,
        last_name: str,
        password: str,
        role: UserRole = UserRole.CUSTOMER,
    ) -> Dict[str, Any]:
        """
        Create a new user.
        Returns: {"success": bool, "user": User or None, "errors": List[str]}
        """
        errors = []

        # Validate email
        if not Validator.validate_email(email):
            errors.append("Invalid email format")

        # Validate username
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters")

        # Check if user exists
        if email.lower() in {u.email.lower() for u in self.users_db.values()}:
            errors.append("Email already registered")

        # Validate password strength
        password_check = Validator.validate_password_strength(password)
        if not password_check["is_strong"]:
            errors.extend(password_check["messages"])

        if errors:
            logger.error("User creation failed", email=email, errors=errors)
            return {"success": False, "user": None, "errors": errors}

        # Create user
        user_id = f"user_{len(self.users_db) + 1}"
        now = datetime.utcnow()

        user = User(
            id=user_id,
            email=email.lower(),
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=True,
            password_hash=PasswordManager.hash_password(password),
            created_at=now,
            updated_at=now,
        )

        self.users_db[user_id] = user
        logger.info("User created successfully", user_id=user_id, email=email, role=role.value)

        return {"success": True, "user": user, "errors": []}

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users_db.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        email_lower = email.lower()
        for user in self.users_db.values():
            if user.email == email_lower:
                return user
        return None

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user with email and password.
        Returns: {"authenticated": bool, "user": User or None, "message": str}
        """
        user = self.get_user_by_email(email)

        if not user:
            logger.warning("Authentication failed: user not found", email=email)
            return {"authenticated": False, "user": None, "message": "Invalid credentials"}

        if not user.is_active:
            logger.warning("Authentication failed: user inactive", user_id=user.id)
            return {"authenticated": False, "user": None, "message": "Account is inactive"}

        if not PasswordManager.verify_password(password, user.password_hash):
            logger.warning("Authentication failed: invalid password", user_id=user.id)
            return {"authenticated": False, "user": None, "message": "Invalid credentials"}

        logger.info("User authenticated successfully", user_id=user.id)
        return {"authenticated": True, "user": user, "message": "Authentication successful"}

    def update_user(self, user_id: str, **updates) -> Optional[User]:
        """Update user information."""
        user = self.get_user(user_id)
        if not user:
            return None

        # Update allowed fields
        allowed_fields = ["first_name", "last_name", "is_active"]
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        logger.info("User updated", user_id=user_id, fields=list(updates.keys()))
        return user

    def delete_user(self, user_id: str) -> bool:
        """Delete a user (soft delete - mark as inactive)."""
        user = self.get_user(user_id)
        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()
        logger.info("User deleted", user_id=user_id)
        return True
