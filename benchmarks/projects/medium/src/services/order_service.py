"""
Order processing service.
Handles order creation, status updates, and fulfillment.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from src.utils.logger import get_logger
from src.models import Order, OrderStatus


logger = get_logger(__name__)


class OrderService:
    """Service for order-related operations."""

    def __init__(self):
        self.orders_db = {}

    def create_order(
        self,
        user_id: str,
        items: List[str],
        total_amount: float,
        shipping_address: str,
    ) -> Dict[str, Any]:
        """
        Create a new order.
        Returns: {"success": bool, "order": Order or None, "errors": List[str]}
        """
        errors = []

        # Validate user ID
        if not user_id:
            errors.append("User ID is required")

        # Validate items
        if not items or len(items) == 0:
            errors.append("Order must contain at least one item")

        # Validate total amount
        if total_amount <= 0:
            errors.append("Order total must be greater than 0")

        # Validate shipping address
        if not shipping_address or len(shipping_address) < 10:
            errors.append("Valid shipping address is required")

        if errors:
            logger.error("Order creation failed", user_id=user_id, errors=errors)
            return {"success": False, "order": None, "errors": errors}

        # Create order
        order_id = f"ord_{len(self.orders_db) + 1}"
        now = datetime.utcnow()

        order = Order(
            id=order_id,
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            items=items,
            shipping_address=shipping_address,
            created_at=now,
            updated_at=now,
        )

        self.orders_db[order_id] = order
        logger.info(
            "Order created successfully",
            order_id=order_id,
            user_id=user_id,
            items_count=len(items),
            total_amount=total_amount,
        )

        return {"success": True, "order": order, "errors": []}

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self.orders_db.get(order_id)

    def get_user_orders(self, user_id: str, limit: int = 50) -> List[Order]:
        """Get all orders for a user."""
        user_orders = [o for o in self.orders_db.values() if o.user_id == user_id]
        return user_orders[:limit]

    def update_order_status(self, order_id: str, status: OrderStatus) -> Optional[Order]:
        """Update order status."""
        order = self.get_order(order_id)
        if not order:
            return None

        old_status = order.status
        order.status = status
        order.updated_at = datetime.utcnow()

        logger.info(
            "Order status updated",
            order_id=order_id,
            old_status=old_status.value,
            new_status=status.value,
        )
        return order

    def confirm_order(self, order_id: str) -> Optional[Order]:
        """Move order from pending to confirmed."""
        return self.update_order_status(order_id, OrderStatus.CONFIRMED)

    def ship_order(self, order_id: str) -> Optional[Order]:
        """Move order to shipped status."""
        return self.update_order_status(order_id, OrderStatus.SHIPPED)

    def deliver_order(self, order_id: str) -> Optional[Order]:
        """Move order to delivered status."""
        return self.update_order_status(order_id, OrderStatus.DELIVERED)

    def cancel_order(self, order_id: str) -> Optional[Order]:
        """Cancel an order."""
        order = self.get_order(order_id)
        if not order:
            return None

        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            logger.warning(
                "Cannot cancel order",
                order_id=order_id,
                reason="Already shipped or delivered",
            )
            return None

        return self.update_order_status(order_id, OrderStatus.CANCELLED)

    def calculate_order_total(self, items: List[Dict[str, Any]]) -> float:
        """Calculate total from items."""
        total = 0.0
        for item in items:
            if "price" in item and "quantity" in item:
                total += item["price"] * item["quantity"]
        return total
