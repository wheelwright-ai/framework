"""
Data models for the e-commerce API.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    VENDOR = "vendor"
    CUSTOMER = "customer"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class User:
    """User model."""
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    password_hash: Optional[str] = None


@dataclass
class Product:
    """Product model."""
    id: str
    name: str
    slug: str
    description: str
    price: float
    stock_quantity: int
    category_id: str
    vendor_id: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Order:
    """Order model."""
    id: str
    user_id: str
    status: OrderStatus
    total_amount: float
    items: List[str]  # Product IDs
    shipping_address: str
    created_at: datetime
    updated_at: datetime


@dataclass
class PaymentMethod:
    """Payment method model."""
    id: str
    user_id: str
    method_type: str  # "card", "bank_account", "wallet"
    is_default: bool
    created_at: datetime
    updated_at: datetime
