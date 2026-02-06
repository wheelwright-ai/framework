"""
User management routes.
Requires authentication.
"""
from typing import Dict, Any


class UserRouter:
    """User management endpoints."""

    def __init__(self, user_service):
        self.user_service = user_service

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """GET /users/{id} - Get user profile."""
        user = self.user_service.get_user(user_id)

        if not user:
            return {"success": False, "message": "User not found", "user": None}

        return {
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            },
        }

    def update_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """PUT /users/{id} - Update user profile."""
        user = self.user_service.update_user(user_id, **data)

        if not user:
            return {"success": False, "message": "User not found"}

        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }

    def list_users(self, role: str = None, limit: int = 50) -> Dict[str, Any]:
        """GET /users - List users."""
        # Note: In a real app, this would query the database
        users = [
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "role": u.role.value,
            }
            for u in self.user_service.users_db.values()
        ]

        if role:
            users = [u for u in users if u["role"] == role]

        return {"success": True, "users": users[:limit], "total": len(users)}

    def deactivate_user(self, user_id: str) -> Dict[str, Any]:
        """DELETE /users/{id} - Deactivate user."""
        success = self.user_service.delete_user(user_id)

        if not success:
            return {"success": False, "message": "User not found"}

        return {"success": True, "message": "User deactivated successfully"}
