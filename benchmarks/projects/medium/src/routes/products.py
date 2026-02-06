"""
Product catalog routes.
Supports both authenticated and unauthenticated access.
"""
from typing import Dict, Any, Optional


class ProductRouter:
    """Product catalog endpoints."""

    def __init__(self, product_service):
        self.product_service = product_service

    def list_products(
        self,
        category_id: Optional[str] = None,
        vendor_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """GET /products - List products."""
        products = self.product_service.list_products(
            category_id=category_id,
            vendor_id=vendor_id,
            limit=limit,
            offset=offset,
        )

        return {
            "success": True,
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "slug": p.slug,
                    "price": p.price,
                    "description": p.description[:100],  # Truncate
                    "stock_quantity": p.stock_quantity,
                }
                for p in products
            ],
            "total": len(list(self.product_service.products_db.values())),
        }

    def get_product(self, product_id: str) -> Dict[str, Any]:
        """GET /products/{id} - Get product details."""
        product = self.product_service.get_product(product_id)

        if not product:
            return {"success": False, "message": "Product not found", "product": None}

        return {
            "success": True,
            "product": {
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "description": product.description,
                "price": product.price,
                "stock_quantity": product.stock_quantity,
                "category_id": product.category_id,
                "vendor_id": product.vendor_id,
                "created_at": product.created_at.isoformat(),
            },
        }

    def create_product(self, data: Dict[str, Any], vendor_id: str) -> Dict[str, Any]:
        """POST /products - Create new product (vendor only)."""
        result = self.product_service.create_product(
            name=data.get("name"),
            description=data.get("description"),
            price=data.get("price"),
            stock_quantity=data.get("stock_quantity", 0),
            category_id=data.get("category_id"),
            vendor_id=vendor_id,
        )

        if result["success"]:
            product = result["product"]
            return {
                "success": True,
                "message": "Product created successfully",
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "slug": product.slug,
                },
            }

        return {
            "success": False,
            "message": "Product creation failed",
            "errors": result["errors"],
        }

    def update_product(
        self,
        product_id: str,
        data: Dict[str, Any],
        vendor_id: str,
    ) -> Dict[str, Any]:
        """PUT /products/{id} - Update product (vendor only)."""
        product = self.product_service.get_product(product_id)

        if not product:
            return {"success": False, "message": "Product not found"}

        if product.vendor_id != vendor_id:
            return {"success": False, "message": "Not authorized to update this product"}

        updated = self.product_service.update_product(product_id, **data)

        if not updated:
            return {"success": False, "message": "Update failed"}

        return {
            "success": True,
            "message": "Product updated successfully",
            "product": {
                "id": updated.id,
                "name": updated.name,
                "price": updated.price,
            },
        }

    def check_availability(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """GET /products/{id}/availability - Check stock."""
        available = self.product_service.check_stock(product_id, quantity)

        product = self.product_service.get_product(product_id)
        if not product:
            return {"success": False, "message": "Product not found"}

        return {
            "success": True,
            "available": available,
            "stock_quantity": product.stock_quantity,
            "requested_quantity": quantity,
        }
