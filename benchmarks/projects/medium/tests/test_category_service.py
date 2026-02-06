"""
Tests for category service.
"""
import pytest
from src.services.category_service import CategoryService


class TestCategoryService:
    """Test category service operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = CategoryService()

    def test_create_category_success(self):
        """Test successful category creation."""
        result = self.service.create_category(
            name="Electronics",
            description="Electronic devices and accessories",
        )
        assert result["success"] is True
        assert result["category"]["name"] == "Electronics"

    def test_create_category_invalid_name(self):
        """Test category creation with invalid name."""
        result = self.service.create_category(
            name="A",
            description="Too short",
        )
        assert result["success"] is False

    def test_get_category_by_slug(self):
        """Test getting category by slug."""
        # Create category
        create_result = self.service.create_category(
            name="Test Category",
            slug="test-category",
        )

        # Get by slug
        category = self.service.get_category_by_slug("test-category")
        assert category is not None
        assert category["name"] == "Test Category"

    def test_list_categories(self):
        """Test listing categories."""
        # Create multiple categories
        for i in range(5):
            self.service.create_category(name=f"Category {i}")

        categories = self.service.list_categories()
        assert len(categories) == 5

    def test_update_category(self):
        """Test updating category."""
        create_result = self.service.create_category(
            name="Original Name",
        )
        category_id = create_result["category"]["id"]

        updated = self.service.update_category(
            category_id, name="Updated Name"
        )
        assert updated["name"] == "Updated Name"

    def test_delete_category(self):
        """Test deleting category."""
        create_result = self.service.create_category(name="Test Category")
        category_id = create_result["category"]["id"]

        success = self.service.delete_category(category_id)
        assert success is True

        # Verify deleted
        assert self.service.get_category(category_id) is None
