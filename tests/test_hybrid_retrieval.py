"""Unit tests for HybridReviewRetriever and Reciprocal Rank Fusion (RRF)."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest

from buywise.engine.hybrid_retrieval import HybridReviewRetriever
from buywise.models.aspect import AspectCategory
from buywise.models.review import ReviewRecord


@pytest.fixture
def sample_reviews() -> list[ReviewRecord]:
    now = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)
    return [
        ReviewRecord(
            review_id="REV-1",
            asin="B0TEST0001",
            rating=Decimal("5.0"),
            title="Incredible battery endurance",
            body="The battery runtime lasts well over 16 hours on a single charge. Outstanding charger.",
            review_date=now,
            is_verified_purchase=True,
            helpful_votes=20,
        ),
        ReviewRecord(
            review_id="REV-2",
            asin="B0TEST0001",
            rating=Decimal("2.0"),
            title="Screen has severe lag and stutter",
            body="The display refresh rate causes lag and visual stutter when scrolling web pages.",
            review_date=now,
            is_verified_purchase=True,
            helpful_votes=5,
        ),
        ReviewRecord(
            review_id="REV-3",
            asin="B0TEST0001",
            rating=Decimal("1.0"),
            title="Hinge broke after two months",
            body="The plastic hinge cracked and broke completely. Catastrophic build quality defect.",
            review_date=now,
            is_verified_purchase=False,
            helpful_votes=50,
        ),
    ]


class TestHybridReviewRetriever:
    """Test suite for BM25 + Semantic RRF hybrid retrieval."""

    def test_search_retrieves_relevant_review(self, sample_reviews: list[ReviewRecord]):
        retriever = HybridReviewRetriever(sample_reviews)
        results = retriever.search("battery charging hours", top_n=2)
        assert len(results) > 0
        top_review, top_score = results[0]
        assert top_review.review_id == "REV-1"
        assert top_score > 0.0

    def test_retrieve_for_aspect_battery(self, sample_reviews: list[ReviewRecord]):
        retriever = HybridReviewRetriever(sample_reviews)
        results = retriever.retrieve_for_aspect(AspectCategory.BATTERY, limit=1)
        assert len(results) == 1
        assert results[0][0].review_id == "REV-1"

    def test_retrieve_for_aspect_defect(self, sample_reviews: list[ReviewRecord]):
        retriever = HybridReviewRetriever(sample_reviews)
        results = retriever.retrieve_for_aspect(AspectCategory.DEFECT, limit=2)
        assert len(results) > 0
        # Either REV-3 (hinge broke) or REV-2 (lag stutter)
        ids = [r[0].review_id for r in results]
        assert "REV-3" in ids

    def test_empty_reviews_returns_empty(self):
        retriever = HybridReviewRetriever([])
        results = retriever.search("battery")
        assert results == []
