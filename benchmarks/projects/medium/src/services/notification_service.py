"""
Notification service for order and user events.
Handles email, SMS, and in-app notifications.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from src.utils.logger import get_logger


logger = get_logger(__name__)


class NotificationType(str, Enum):
    """Types of notifications."""
    ORDER_CONFIRMATION = "order_confirmation"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    PAYMENT_RECEIVED = "payment_received"
    LOW_STOCK = "low_stock"
    NEW_REVIEW = "new_review"


class NotificationService:
    """Service for managing notifications."""

    def __init__(self):
        self.notifications_db = {}
        self.preferences_db = {}

    def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a notification to a user.
        Returns: {"success": bool, "notification_id": str or None}
        """
        notification_id = f"notif_{len(self.notifications_db) + 1}"

        notification = {
            "id": notification_id,
            "user_id": user_id,
            "type": notification_type.value,
            "title": title,
            "message": message,
            "data": data or {},
            "is_read": False,
            "created_at": datetime.utcnow(),
        }

        self.notifications_db[notification_id] = notification
        logger.info(
            "Notification sent",
            notification_id=notification_id,
            user_id=user_id,
            type=notification_type.value,
        )

        return {"success": True, "notification_id": notification_id}

    def get_user_notifications(
        self, user_id: str, unread_only: bool = False, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user."""
        notifications = [
            n for n in self.notifications_db.values() if n["user_id"] == user_id
        ]

        if unread_only:
            notifications = [n for n in notifications if not n["is_read"]]

        return notifications[:limit]

    def mark_as_read(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Mark notification as read."""
        notification = self.notifications_db.get(notification_id)
        if not notification:
            return None

        notification["is_read"] = True
        logger.info("Notification marked as read", notification_id=notification_id)
        return notification

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all user notifications as read."""
        count = 0
        for notification in self.notifications_db.values():
            if notification["user_id"] == user_id and not notification["is_read"]:
                notification["is_read"] = True
                count += 1

        logger.info("Marked notifications as read", user_id=user_id, count=count)
        return count

    def set_notification_preference(
        self,
        user_id: str,
        notification_type: NotificationType,
        enabled: bool = True,
        channel: str = "email",
    ) -> Dict[str, Any]:
        """Set user's notification preferences."""
        pref_key = f"{user_id}_{notification_type.value}"

        self.preferences_db[pref_key] = {
            "user_id": user_id,
            "notification_type": notification_type.value,
            "enabled": enabled,
            "channel": channel,
        }

        return self.preferences_db[pref_key]

    def should_send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
    ) -> bool:
        """Check if notification should be sent based on preferences."""
        pref_key = f"{user_id}_{notification_type.value}"
        pref = self.preferences_db.get(pref_key)

        if not pref:
            return True  # Default to enabled

        return pref.get("enabled", True)
