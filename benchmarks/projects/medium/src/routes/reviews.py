"""
Product review routes.
Handles review creation, listing, and management.
"""
from typing import Dict, Any


class ReviewRouter:
    """Review management endpoints."""

    def __init__(self, review_service):
        self.review_service = review_service

    def get_product_reviews(
        self, product_id: str, limit: int = 50
    ) -> Dict[str, Any]:
        """GET /products/{id}/reviews - Get product reviews."""
        reviews = self.review_service.get_product_reviews(product_id, limit)
        rating = self.review_service.get_product_rating(product_id)

        return {
            "success": True,
            "product_id": product_id,
            "reviews": reviews,
            "rating": rating,
            "total": len(reviews),
        }

    def create_review(
        self,
        product_id: str,
        user_id: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """POST /products/{id}/reviews - Create product review."""
        result = self.review_service.create_review(
            product_id=product_id,
            user_id=user_id,
            rating=data.get("rating"),
            title=data.get("title"),
            content=data.get("content"),
        )

        if result["success"]:
            return {
                "success": True,
                "message": "Review created successfully",
                "review": result["review"],
            }

        return {
            "success": False,
            "message": "Review creation failed",
            "errors": result["errors"],
        }

    def get_review(self, review_id: str) -> Dict[str, Any]:
        """GET /reviews/{id} - Get review details."""
        review = self.review_service.get_review(review_id)

        if not review:
            return {"success": False, "message": "Review not found", "review": None}

        return {"success": True, "review": review}

    def update_review(
        self,
        review_id: str,
        user_id: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """PUT /reviews/{id} - Update review."""
        review = self.review_service.update_review(review_id, user_id, **data)

        if not review:
            return {
                "success": False,
                "message": "Review not found or not authorized",
            }

        return {
            "success": True,
            "message": "Review updated successfully",
            "review": review,
        }

    def delete_review(self, review_id: str, user_id: str) -> Dict[str, Any]:
        """DELETE /reviews/{id} - Delete review."""
        success = self.review_service.delete_review(review_id, user_id)

        if not success:
            return {
                "success": False,
                "message": "Review not found or not authorized",
            }

        return {"success": True, "message": "Review deleted successfully"}

    def mark_helpful(self, review_id: str) -> Dict[str, Any]:
        """POST /reviews/{id}/helpful - Mark review as helpful."""
        review = self.review_service.mark_helpful(review_id)

        if not review:
            return {"success": False, "message": "Review not found"}

        return {
            "success": True,
            "message": "Review marked as helpful",
            "helpful_count": review["helpful_count"],
        }
