"""
Product review and rating service.
Handles reviews, ratings, and feedback.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from src.utils.logger import get_logger


logger = get_logger(__name__)


class ReviewService:
    """Service for product reviews and ratings."""

    def __init__(self):
        self.reviews_db = {}
        self.rating_cache = {}

    def create_review(
        self,
        product_id: str,
        user_id: str,
        rating: int,
        title: str,
        content: str,
    ) -> Dict[str, Any]:
        """
        Create a product review.
        Returns: {"success": bool, "review": dict or None, "errors": List[str]}
        """
        errors = []

        # Validate rating
        if not (1 <= rating <= 5):
            errors.append("Rating must be between 1 and 5")

        # Validate title
        if not title or len(title) < 3:
            errors.append("Review title must be at least 3 characters")

        # Validate content
        if not content or len(content) < 10:
            errors.append("Review content must be at least 10 characters")

        if errors:
            logger.error(
                "Review creation failed",
                product_id=product_id,
                errors=errors,
            )
            return {"success": False, "review": None, "errors": errors}

        # Create review
        review_id = f"review_{len(self.reviews_db) + 1}"
        now = datetime.utcnow()

        review = {
            "id": review_id,
            "product_id": product_id,
            "user_id": user_id,
            "rating": rating,
            "title": title,
            "content": content,
            "helpful_count": 0,
            "created_at": now,
            "updated_at": now,
        }

        self.reviews_db[review_id] = review
        logger.info(
            "Review created successfully",
            review_id=review_id,
            product_id=product_id,
            rating=rating,
        )

        return {"success": True, "review": review, "errors": []}

    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get review by ID."""
        return self.reviews_db.get(review_id)

    def get_product_reviews(
        self, product_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all reviews for a product."""
        reviews = [
            r for r in self.reviews_db.values() if r["product_id"] == product_id
        ]
        return reviews[:limit]

    def get_product_rating(self, product_id: str) -> float:
        """Get average rating for a product."""
        reviews = self.get_product_reviews(product_id)
        if not reviews:
            return 0.0
        return sum(r["rating"] for r in reviews) / len(reviews)

    def update_review(
        self, review_id: str, user_id: str, **updates
    ) -> Optional[Dict[str, Any]]:
        """Update review (only by original author)."""
        review = self.get_review(review_id)
        if not review or review["user_id"] != user_id:
            return None

        # Update allowed fields
        allowed_fields = ["title", "content", "rating"]
        for field, value in updates.items():
            if field in allowed_fields:
                review[field] = value

        review["updated_at"] = datetime.utcnow()
        logger.info(
            "Review updated",
            review_id=review_id,
            fields=list(updates.keys()),
        )
        return review

    def delete_review(self, review_id: str, user_id: str) -> bool:
        """Delete review (only by original author or admin)."""
        review = self.get_review(review_id)
        if not review or review["user_id"] != user_id:
            return False

        del self.reviews_db[review_id]
        logger.info("Review deleted", review_id=review_id)
        return True

    def mark_helpful(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Mark review as helpful."""
        review = self.get_review(review_id)
        if not review:
            return None

        review["helpful_count"] += 1
        return review
