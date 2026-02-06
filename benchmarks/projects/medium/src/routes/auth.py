"""
Authentication routes.
Handles user registration, login, and token management.
"""
from typing import Dict, Any
from datetime import datetime, timedelta
import json


class AuthRouter:
    """Authentication endpoints."""

    def __init__(self, user_service, config):
        self.user_service = user_service
        self.config = config
        self.tokens = {}  # Store issued tokens

    def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /auth/register - Register new user."""
        result = self.user_service.create_user(
            email=data.get("email"),
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            password=data.get("password"),
        )

        if result["success"]:
            user = result["user"]
            return {
                "success": True,
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                },
            }

        return {
            "success": False,
            "message": "Registration failed",
            "errors": result["errors"],
        }

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """POST /auth/login - Authenticate user and issue token."""
        auth_result = self.user_service.authenticate_user(email, password)

        if not auth_result["authenticated"]:
            return {
                "success": False,
                "message": auth_result["message"],
                "token": None,
            }

        user = auth_result["user"]
        # Mock JWT token generation
        token = f"jwt_token_{user.id}_{int(datetime.utcnow().timestamp())}"
        self.tokens[token] = {
            "user_id": user.id,
            "issued_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=self.config.jwt.expiration_minutes),
        }

        return {
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role.value,
            },
        }

    def logout(self, token: str) -> Dict[str, Any]:
        """POST /auth/logout - Invalidate token."""
        if token in self.tokens:
            del self.tokens[token]
            return {"success": True, "message": "Logged out successfully"}

        return {"success": False, "message": "Invalid token"}

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify if a token is valid."""
        if token not in self.tokens:
            return {"valid": False, "user_id": None}

        token_data = self.tokens[token]
        if datetime.utcnow() > token_data["expires_at"]:
            del self.tokens[token]
            return {"valid": False, "user_id": None}

        return {"valid": True, "user_id": token_data["user_id"]}

    def refresh_token(self, old_token: str) -> Dict[str, Any]:
        """POST /auth/refresh - Get new token."""
        if old_token not in self.tokens:
            return {"success": False, "new_token": None, "message": "Invalid token"}

        token_data = self.tokens[old_token]
        user_id = token_data["user_id"]

        # Issue new token
        new_token = f"jwt_token_{user_id}_{int(datetime.utcnow().timestamp())}"
        self.tokens[new_token] = {
            "user_id": user_id,
            "issued_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=self.config.jwt.expiration_minutes),
        }

        # Optionally invalidate old token
        del self.tokens[old_token]

        return {
            "success": True,
            "new_token": new_token,
            "message": "Token refreshed successfully",
        }
