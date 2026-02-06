"""
Tests for product service.
"""
import pytest
from src.services.product_service import ProductService


class TestProductService:
    """Test product service operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ProductService()

    def test_create_product_success(self):
        """Test successful product creation."""
        result = self.service.create_product(
            name="Test Product",
            description="A test product",
            price=99.99,
            stock_quantity=100,
            category_id="cat_1",
            vendor_id="vendor_1",
        )
        assert result["success"] is True
        assert result["product"].name == "Test Product"

    def test_create_product_invalid_price(self):
        """Test product creation with invalid price."""
        result = self.service.create_product(
            name="Test Product",
            description="A test product",
            price=-10,
            stock_quantity=100,
            category_id="cat_1",
            vendor_id="vendor_1",
        )
        assert result["success"] is False

    def test_get_product_by_slug(self):
        """Test getting product by slug."""
        # Create product
        create_result = self.service.create_product(
            name="Test Product",
            description="A test product",
            price=99.99,
            stock_quantity=100,
            category_id="cat_1",
            vendor_id="vendor_1",
        )

        # Get by slug
        product = self.service.get_product_by_slug("test-product")
        assert product is not None
        assert product.name == "Test Product"

    def test_check_stock_sufficient(self):
        """Test checking sufficient stock."""
        product_id = self.service.create_product(
            name="Test Product",
            description="A test product",
            price=99.99,
            stock_quantity=100,
            category_id="cat_1",
            vendor_id="vendor_1",
        )["product"].id

        available = self.service.check_stock(product_id, 50)
        assert available is True

    def test_check_stock_insufficient(self):
        """Test checking insufficient stock."""
        product_id = self.service.create_product(
            name="Test Product",
            description="A test product",
            price=99.99,
            stock_quantity=100,
            category_id="cat_1",
            vendor_id="vendor_1",
        )["product"].id

        available = self.service.check_stock(product_id, 150)
        assert available is False

    def test_reserve_stock(self):
        """Test reserving stock."""
        product_id = self.service.create_product(
            name="Test Product",
            description="A test product",
            price=99.99,
            stock_quantity=100,
            category_id="cat_1",
            vendor_id="vendor_1",
        )["product"].id

        success = self.service.reserve_stock(product_id, 50)
        assert success is True

        # Check remaining stock
        product = self.service.get_product(product_id)
        assert product.stock_quantity == 50

    def test_list_products_with_filter(self):
        """Test listing products with filters."""
        # Create multiple products
        for i in range(5):
            self.service.create_product(
                name=f"Product {i}",
                description="Test product",
                price=99.99,
                stock_quantity=100,
                category_id="cat_1" if i < 3 else "cat_2",
                vendor_id="vendor_1",
            )

        # List with category filter
        products = self.service.list_products(category_id="cat_1")
        assert len(products) == 3
