"""
Product category routes.
Supports both authenticated and unauthenticated access.
"""
from typing import Dict, Any, Optional


class CategoryRouter:
    """Category management endpoints."""

    def __init__(self, category_service):
        self.category_service = category_service

    def list_categories(self, limit: int = 100) -> Dict[str, Any]:
        """GET /categories - List product categories."""
        categories = self.category_service.list_categories(limit)

        return {
            "success": True,
            "categories": categories,
            "total": len(list(self.category_service.categories_db.values())),
        }

    def get_category(self, category_id: str) -> Dict[str, Any]:
        """GET /categories/{id} - Get category details."""
        category = self.category_service.get_category(category_id)

        if not category:
            return {
                "success": False,
                "message": "Category not found",
                "category": None,
            }

        return {"success": True, "category": category}

    def create_category(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /categories - Create new category (admin only)."""
        result = self.category_service.create_category(
            name=data.get("name"),
            description=data.get("description", ""),
            slug=data.get("slug", ""),
        )

        if result["success"]:
            return {
                "success": True,
                "message": "Category created successfully",
                "category": result["category"],
            }

        return {
            "success": False,
            "message": "Category creation failed",
            "errors": result["errors"],
        }

    def update_category(
        self, category_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """PUT /categories/{id} - Update category (admin only)."""
        category = self.category_service.update_category(category_id, **data)

        if not category:
            return {"success": False, "message": "Category not found"}

        return {
            "success": True,
            "message": "Category updated successfully",
            "category": category,
        }

    def delete_category(self, category_id: str) -> Dict[str, Any]:
        """DELETE /categories/{id} - Delete category (admin only)."""
        success = self.category_service.delete_category(category_id)

        if not success:
            return {
                "success": False,
                "message": "Cannot delete category (has products or not found)",
            }

        return {"success": True, "message": "Category deleted successfully"}
