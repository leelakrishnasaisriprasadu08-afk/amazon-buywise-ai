"""Unit tests for ReviewAspectAnalyzer and grounded citation binding."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest

from buywise.engine.aspect_analyzer import ReviewAspectAnalyzer
from buywise.models.aspect import AspectCategory, SentimentPolarity
from buywise.models.review import ReviewRecord


@pytest.fixture
def laptop_reviews() -> list[ReviewRecord]:
    now = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)
    return [
        ReviewRecord(
            review_id="REV-M1-1",
            asin="B08N5WRWNW",
            rating=Decimal("5.0"),
            title="Silent and extraordinary battery",
            body="Battery easily lasts 16 hours. The M1 chip is completely silent without fan noise.",
            review_date=now,
            is_verified_purchase=True,
            helpful_votes=20,
        ),
        ReviewRecord(
            review_id="REV-M1-2",
            asin="B08N5WRWNW",
            rating=Decimal("4.0"),
            title="Crisp display and solid build",
            body="Screen brightness is great and aluminum chassis feels very sturdy and durable.",
            review_date=now,
            is_verified_purchase=True,
            helpful_votes=15,
        ),
        ReviewRecord(
            review_id="REV-M1-3",
            asin="B08N5WRWNW",
            rating=Decimal("1.0"),
            title="Screen cracked spontaneously",
            body="The glass screen cracked near the bottom bezel. Disappointing failure.",
            review_date=now,
            is_verified_purchase=True,
            helpful_votes=12,
        ),
    ]


class TestReviewAspectAnalyzer:
    """Test suite for aspect sentiment classification and grounded citation binding."""

    def test_aspect_analysis_sentiment_and_citations(self, laptop_reviews: list[ReviewRecord]):
        analyzer = ReviewAspectAnalyzer()
        analysis = analyzer.analyze("B08N5WRWNW", laptop_reviews)

        assert analysis.asin == "B08N5WRWNW"
        assert analysis.total_reviews_analyzed == 3
        assert analysis.verified_review_ratio == 1.0

        # Battery aspect check
        battery_asp = analysis.aspects.get(AspectCategory.BATTERY)
        assert battery_asp is not None
        assert battery_asp.sentiment == SentimentPolarity.POSITIVE
        assert len(battery_asp.citations) > 0
        assert "REV-M1-1" in [c.review_id for c in battery_asp.citations]

        # Defect rate check
        assert analysis.defect_rate > 0.0
        assert len(analysis.critical_defects) > 0

    def test_empty_reviews_analysis(self):
        analyzer = ReviewAspectAnalyzer()
        analysis = analyzer.analyze("B0EMPTY000", [])
        assert analysis.total_reviews_analyzed == 0
        assert analysis.aspects == {}
        assert analysis.defect_rate == 0.0
