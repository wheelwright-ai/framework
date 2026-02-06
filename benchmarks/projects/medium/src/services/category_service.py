"""
Product category management service.
Handles category creation, organization, and listing.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from src.utils.logger import get_logger


logger = get_logger(__name__)


class CategoryService:
    """Service for category-related operations."""

    def __init__(self):
        self.categories_db = {}

    def create_category(
        self,
        name: str,
        description: str = "",
        slug: str = "",
    ) -> Dict[str, Any]:
        """
        Create a new product category.
        Returns: {"success": bool, "category": dict or None, "errors": List[str]}
        """
        errors = []

        # Validate name
        if not name or len(name) < 2:
            errors.append("Category name must be at least 2 characters")

        # Create slug if not provided
        if not slug:
            slug = name.lower().replace(" ", "-")

        if errors:
            logger.error("Category creation failed", name=name, errors=errors)
            return {"success": False, "category": None, "errors": errors}

        # Create category
        category_id = f"cat_{len(self.categories_db) + 1}"
        now = datetime.utcnow()

        category = {
            "id": category_id,
            "name": name,
            "description": description,
            "slug": slug,
            "created_at": now,
            "updated_at": now,
            "product_count": 0,
        }

        self.categories_db[category_id] = category
        logger.info(
            "Category created successfully",
            category_id=category_id,
            name=name,
        )

        return {"success": True, "category": category, "errors": []}

    def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Get category by ID."""
        return self.categories_db.get(category_id)

    def get_category_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get category by slug."""
        for category in self.categories_db.values():
            if category["slug"] == slug:
                return category
        return None

    def list_categories(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all categories."""
        categories = list(self.categories_db.values())
        return categories[:limit]

    def update_category(
        self, category_id: str, **updates
    ) -> Optional[Dict[str, Any]]:
        """Update category information."""
        category = self.get_category(category_id)
        if not category:
            return None

        # Update allowed fields
        allowed_fields = ["name", "description"]
        for field, value in updates.items():
            if field in allowed_fields:
                category[field] = value

        category["updated_at"] = datetime.utcnow()
        logger.info(
            "Category updated",
            category_id=category_id,
            fields=list(updates.keys()),
        )
        return category

    def delete_category(self, category_id: str) -> bool:
        """Delete a category (if no products)."""
        category = self.get_category(category_id)
        if not category:
            return False

        if category.get("product_count", 0) > 0:
            logger.warning(
                "Cannot delete category with products",
                category_id=category_id,
            )
            return False

        del self.categories_db[category_id]
        logger.info("Category deleted", category_id=category_id)
        return True
