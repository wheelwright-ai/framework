"""
Payment processing routes.
Requires authentication.
"""
from typing import Dict, Any


class PaymentRouter:
    """Payment processing endpoints."""

    def __init__(self, payment_service, order_service):
        self.payment_service = payment_service
        self.order_service = order_service

    def create_payment(
        self,
        user_id: str,
        order_id: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """POST /payments - Process payment for order."""
        # Verify order exists and belongs to user
        order = self.order_service.get_order(order_id)

        if not order:
            return {"success": False, "message": "Order not found"}

        if order.user_id != user_id:
            return {"success": False, "message": "Not authorized"}

        # Verify payment method
        payment_method_id = data.get("payment_method_id")
        if not self.payment_service.verify_payment_method(payment_method_id, user_id):
            return {"success": False, "message": "Invalid payment method"}

        # Process payment
        result = self.payment_service.process_payment(
            order_id=order_id,
            user_id=user_id,
            amount=order.total_amount,
            payment_method_id=payment_method_id,
        )

        return result

    def get_payment(self, transaction_id: str) -> Dict[str, Any]:
        """GET /payments/{id} - Get payment details."""
        transaction = self.payment_service.get_transaction(transaction_id)

        if not transaction:
            return {"success": False, "message": "Payment not found"}

        return {
            "success": True,
            "payment": {
                "transaction_id": transaction_id,
                "order_id": transaction.get("order_id"),
                "amount": transaction.get("amount"),
                "status": transaction.get("status"),
                "created_at": transaction.get("created_at"),
            },
        }

    def refund_payment(
        self,
        transaction_id: str,
        user_id: str,
        reason: str = "Customer request",
    ) -> Dict[str, Any]:
        """POST /payments/{id}/refund - Refund a payment."""
        transaction = self.payment_service.get_transaction(transaction_id)

        if not transaction:
            return {"success": False, "message": "Payment not found"}

        if transaction.get("user_id") != user_id:
            return {"success": False, "message": "Not authorized"}

        result = self.payment_service.process_refund(transaction_id, reason)

        return result
