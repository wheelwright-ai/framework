"""
Tests for order service.
"""
import pytest
from src.services.order_service import OrderService
from src.models import OrderStatus


class TestOrderService:
    """Test order service operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = OrderService()

    def test_create_order_success(self):
        """Test successful order creation."""
        result = self.service.create_order(
            user_id="user_1",
            items=["prod_1", "prod_2"],
            total_amount=199.99,
            shipping_address="123 Main St, City, State 12345",
        )
        assert result["success"] is True
        assert result["order"].status == OrderStatus.PENDING

    def test_create_order_missing_items(self):
        """Test order creation without items."""
        result = self.service.create_order(
            user_id="user_1",
            items=[],
            total_amount=199.99,
            shipping_address="123 Main St, City, State 12345",
        )
        assert result["success"] is False

    def test_create_order_invalid_amount(self):
        """Test order creation with invalid amount."""
        result = self.service.create_order(
            user_id="user_1",
            items=["prod_1"],
            total_amount=-50,
            shipping_address="123 Main St, City, State 12345",
        )
        assert result["success"] is False

    def test_get_user_orders(self):
        """Test getting user's orders."""
        # Create multiple orders
        for i in range(3):
            self.service.create_order(
                user_id="user_1",
                items=[f"prod_{i}"],
                total_amount=100.0 + i,
                shipping_address="123 Main St, City, State 12345",
            )

        orders = self.service.get_user_orders("user_1")
        assert len(orders) == 3

    def test_update_order_status(self):
        """Test updating order status."""
        # Create order
        create_result = self.service.create_order(
            user_id="user_1",
            items=["prod_1"],
            total_amount=99.99,
            shipping_address="123 Main St, City, State 12345",
        )
        order_id = create_result["order"].id

        # Update status
        updated = self.service.update_order_status(order_id, OrderStatus.CONFIRMED)
        assert updated.status == OrderStatus.CONFIRMED

    def test_confirm_order(self):
        """Test confirming an order."""
        create_result = self.service.create_order(
            user_id="user_1",
            items=["prod_1"],
            total_amount=99.99,
            shipping_address="123 Main St, City, State 12345",
        )
        order_id = create_result["order"].id

        confirmed = self.service.confirm_order(order_id)
        assert confirmed.status == OrderStatus.CONFIRMED

    def test_cancel_order_pending(self):
        """Test cancelling a pending order."""
        create_result = self.service.create_order(
            user_id="user_1",
            items=["prod_1"],
            total_amount=99.99,
            shipping_address="123 Main St, City, State 12345",
        )
        order_id = create_result["order"].id

        cancelled = self.service.cancel_order(order_id)
        assert cancelled is not None
        assert cancelled.status == OrderStatus.CANCELLED

    def test_calculate_order_total(self):
        """Test calculating order total."""
        items = [
            {"price": 10.0, "quantity": 2},
            {"price": 20.0, "quantity": 1},
        ]
        total = self.service.calculate_order_total(items)
        assert total == 40.0
