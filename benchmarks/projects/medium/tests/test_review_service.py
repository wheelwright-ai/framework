"""
Tests for review service.
"""
import pytest
from src.services.review_service import ReviewService


class TestReviewService:
    """Test review service operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ReviewService()

    def test_create_review_success(self):
        """Test successful review creation."""
        result = self.service.create_review(
            product_id="prod_1",
            user_id="user_1",
            rating=5,
            title="Great product!",
            content="This product is amazing and highly recommended for everyone.",
        )
        assert result["success"] is True
        assert result["review"]["rating"] == 5

    def test_create_review_invalid_rating(self):
        """Test review creation with invalid rating."""
        result = self.service.create_review(
            product_id="prod_1",
            user_id="user_1",
            rating=10,
            title="Good product",
            content="This is a good product with great features.",
        )
        assert result["success"] is False

    def test_create_review_short_content(self):
        """Test review creation with short content."""
        result = self.service.create_review(
            product_id="prod_1",
            user_id="user_1",
            rating=4,
            title="OK",
            content="OK",
        )
        assert result["success"] is False

    def test_get_product_reviews(self):
        """Test getting product reviews."""
        # Create multiple reviews
        for i in range(3):
            self.service.create_review(
                product_id="prod_1",
                user_id=f"user_{i}",
                rating=i + 3,
                title=f"Review {i}",
                content=f"This is review number {i} with detailed content.",
            )

        reviews = self.service.get_product_reviews("prod_1")
        assert len(reviews) == 3

    def test_get_product_rating(self):
        """Test calculating product rating."""
        # Create reviews with known ratings
        self.service.create_review(
            product_id="prod_1",
            user_id="user_1",
            rating=5,
            title="Great",
            content="This is a great product to recommend.",
        )
        self.service.create_review(
            product_id="prod_1",
            user_id="user_2",
            rating=3,
            title="OK",
            content="This product is okay but could be better.",
        )

        rating = self.service.get_product_rating("prod_1")
        assert rating == 4.0

    def test_update_review(self):
        """Test updating review."""
        create_result = self.service.create_review(
            product_id="prod_1",
            user_id="user_1",
            rating=3,
            title="Original",
            content="This is the original review content.",
        )
        review_id = create_result["review"]["id"]

        updated = self.service.update_review(
            review_id,
            "user_1",
            rating=5,
            title="Updated",
        )
        assert updated["rating"] == 5
        assert updated["title"] == "Updated"

    def test_delete_review(self):
        """Test deleting review."""
        create_result = self.service.create_review(
            product_id="prod_1",
            user_id="user_1",
            rating=4,
            title="Test Review",
            content="This is a test review to be deleted.",
        )
        review_id = create_result["review"]["id"]

        success = self.service.delete_review(review_id, "user_1")
        assert success is True

        # Verify deleted
        assert self.service.get_review(review_id) is None

    def test_mark_helpful(self):
        """Test marking review as helpful."""
        create_result = self.service.create_review(
            product_id="prod_1",
            user_id="user_1",
            rating=5,
            title="Helpful Review",
            content="This is a very helpful and detailed review.",
        )
        review_id = create_result["review"]["id"]

        result = self.service.mark_helpful(review_id)
        assert result["helpful_count"] == 1
