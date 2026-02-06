"""
Product catalog service.
Manages product listings, inventory, and search.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.validation import Validator
from src.models import Product


logger = get_logger(__name__)


class ProductService:
    """Service for product-related operations."""

    def __init__(self):
        self.products_db = {}
        self.categories_db = {}

    def create_product(
        self,
        name: str,
        description: str,
        price: float,
        stock_quantity: int,
        category_id: str,
        vendor_id: str,
    ) -> Dict[str, Any]:
        """
        Create a new product.
        Returns: {"success": bool, "product": Product or None, "errors": List[str]}
        """
        errors = []

        # Validate product name
        if not name or len(name) < 3:
            errors.append("Product name must be at least 3 characters")

        # Validate price
        if price <= 0:
            errors.append("Price must be greater than 0")

        # Validate stock
        if stock_quantity < 0:
            errors.append("Stock quantity cannot be negative")

        # Create slug
        slug = name.lower().replace(" ", "-")
        if not Validator.validate_slug(slug):
            errors.append("Invalid product name for URL slug")

        if errors:
            logger.error("Product creation failed", name=name, errors=errors)
            return {"success": False, "product": None, "errors": errors}

        # Create product
        product_id = f"prod_{len(self.products_db) + 1}"
        now = datetime.utcnow()

        product = Product(
            id=product_id,
            name=name,
            slug=slug,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            category_id=category_id,
            vendor_id=vendor_id,
            created_at=now,
            updated_at=now,
        )

        self.products_db[product_id] = product
        logger.info(
            "Product created successfully",
            product_id=product_id,
            name=name,
            vendor_id=vendor_id,
        )

        return {"success": True, "product": product, "errors": []}

    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        return self.products_db.get(product_id)

    def get_product_by_slug(self, slug: str) -> Optional[Product]:
        """Get product by slug."""
        for product in self.products_db.values():
            if product.slug == slug:
                return product
        return None

    def list_products(
        self,
        category_id: Optional[str] = None,
        vendor_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Product]:
        """List products with optional filters."""
        results = list(self.products_db.values())

        if category_id:
            results = [p for p in results if p.category_id == category_id]

        if vendor_id:
            results = [p for p in results if p.vendor_id == vendor_id]

        return results[offset : offset + limit]

    def update_product(self, product_id: str, **updates) -> Optional[Product]:
        """Update product information."""
        product = self.get_product(product_id)
        if not product:
            return None

        # Validate price if provided
        if "price" in updates and updates["price"] <= 0:
            logger.error("Invalid price for product update", product_id=product_id)
            return None

        # Validate stock if provided
        if "stock_quantity" in updates and updates["stock_quantity"] < 0:
            logger.error("Invalid stock quantity", product_id=product_id)
            return None

        # Update allowed fields
        allowed_fields = ["name", "description", "price", "stock_quantity"]
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(product, field, value)

        product.updated_at = datetime.utcnow()
        logger.info("Product updated", product_id=product_id, fields=list(updates.keys()))
        return product

    def check_stock(self, product_id: str, quantity: int) -> bool:
        """Check if sufficient stock is available."""
        product = self.get_product(product_id)
        if not product:
            return False
        return product.stock_quantity >= quantity

    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        """Reserve stock for an order."""
        product = self.get_product(product_id)
        if not product or not self.check_stock(product_id, quantity):
            logger.warning(
                "Stock reservation failed",
                product_id=product_id,
                requested=quantity,
                available=product.stock_quantity if product else 0,
            )
            return False

        product.stock_quantity -= quantity
        logger.info(
            "Stock reserved",
            product_id=product_id,
            quantity=quantity,
            remaining=product.stock_quantity,
        )
        return True
