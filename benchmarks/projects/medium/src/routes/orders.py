"""
Order management routes.
Requires authentication.
"""
from typing import Dict, Any


class OrderRouter:
    """Order management endpoints."""

    def __init__(self, order_service, product_service):
        self.order_service = order_service
        self.product_service = product_service

    def create_order(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /orders - Create new order."""
        # Validate items exist and have stock
        items = data.get("items", [])
        total_amount = 0.0

        for item in items:
            product = self.product_service.get_product(item.get("product_id"))
            if not product:
                return {
                    "success": False,
                    "message": f"Product {item.get('product_id')} not found",
                }

            if not self.product_service.check_stock(
                item.get("product_id"), item.get("quantity", 1)
            ):
                return {
                    "success": False,
                    "message": f"Insufficient stock for product {product.name}",
                }

            total_amount += product.price * item.get("quantity", 1)

        result = self.order_service.create_order(
            user_id=user_id,
            items=[item.get("product_id") for item in items],
            total_amount=total_amount,
            shipping_address=data.get("shipping_address"),
        )

        if result["success"]:
            order = result["order"]
            return {
                "success": True,
                "message": "Order created successfully",
                "order": {
                    "id": order.id,
                    "status": order.status.value,
                    "total_amount": order.total_amount,
                },
            }

        return {
            "success": False,
            "message": "Order creation failed",
            "errors": result["errors"],
        }

    def get_order(self, order_id: str, user_id: str) -> Dict[str, Any]:
        """GET /orders/{id} - Get order details."""
        order = self.order_service.get_order(order_id)

        if not order:
            return {"success": False, "message": "Order not found", "order": None}

        if order.user_id != user_id:
            return {"success": False, "message": "Not authorized to view this order"}

        return {
            "success": True,
            "order": {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status.value,
                "total_amount": order.total_amount,
                "items": order.items,
                "shipping_address": order.shipping_address,
                "created_at": order.created_at.isoformat(),
            },
        }

    def list_orders(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """GET /orders - List user's orders."""
        orders = self.order_service.get_user_orders(user_id, limit)

        return {
            "success": True,
            "orders": [
                {
                    "id": o.id,
                    "status": o.status.value,
                    "total_amount": o.total_amount,
                    "created_at": o.created_at.isoformat(),
                }
                for o in orders
            ],
            "total": len(orders),
        }

    def update_order_status(
        self,
        order_id: str,
        status: str,
        user_role: str,
    ) -> Dict[str, Any]:
        """PUT /orders/{id}/status - Update order status."""
        # Only admin or vendor can update status (future)
        from src.models import OrderStatus

        try:
            new_status = OrderStatus[status.upper()]
        except KeyError:
            return {"success": False, "message": f"Invalid status: {status}"}

        order = self.order_service.update_order_status(order_id, new_status)

        if not order:
            return {"success": False, "message": "Order not found"}

        return {
            "success": True,
            "message": f"Order status updated to {status}",
            "order": {
                "id": order.id,
                "status": order.status.value,
                "updated_at": order.updated_at.isoformat(),
            },
        }

    def cancel_order(self, order_id: str, user_id: str) -> Dict[str, Any]:
        """DELETE /orders/{id} - Cancel order."""
        order = self.order_service.get_order(order_id)

        if not order:
            return {"success": False, "message": "Order not found"}

        if order.user_id != user_id:
            return {"success": False, "message": "Not authorized"}

        cancelled = self.order_service.cancel_order(order_id)

        if not cancelled:
            return {
                "success": False,
                "message": "Cannot cancel order in current status",
            }

        return {"success": True, "message": "Order cancelled successfully"}
