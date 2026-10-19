"""Unit tests for CompetitorComparisonEngine using the college student laptop case study."""

from decimal import Decimal
import pytest

from buywise.engine.aspect_analyzer import ReviewAspectAnalyzer
from buywise.engine.competitor_matcher import CompetitorComparisonEngine
from buywise.providers.mock_provider import MockFixtureProvider


class TestCompetitorComparisonEngine:
    """Test suite evaluating head-to-head competitor comparison and strictly better logic."""

    def test_college_laptop_alternative_comparison(self, mock_provider: MockFixtureProvider):
        # 1. Fetch Target Laptop (B0COLLEGE1: VendorX SlimBook 14)
        target_prod = mock_provider.get_product("B0COLLEGE1").payload
        target_reviews = mock_provider.get_reviews("B0COLLEGE1").payload
        target_price = Decimal("52000.00")

        # 2. Fetch Alternative Laptop (B0COLLEGE2: BenchmarkPro 14)
        alt_prod = mock_provider.get_product("B0COLLEGE2").payload
        alt_reviews = mock_provider.get_reviews("B0COLLEGE2").payload
        alt_price = Decimal("49990.00")

        # 3. Analyze reviews for both
        analyzer = ReviewAspectAnalyzer()
        target_analysis = analyzer.analyze("B0COLLEGE1", target_reviews)
        alt_analysis = analyzer.analyze("B0COLLEGE2", alt_reviews)

        # 4. Compare products
        engine = CompetitorComparisonEngine()
        rec = engine.compare_products(
            target_product=target_prod,
            target_price=target_price,
            target_analysis=target_analysis,
            alternative_product=alt_prod,
            alternative_price=alt_price,
            alternative_analysis=alt_analysis,
            currency="INR",
        )

        assert rec.target_asin == "B0COLLEGE1"
        assert rec.alternative_asin == "B0COLLEGE2"
        assert rec.price_delta == Decimal("2010.00")  # Saves ₹2,010
        assert rec.currency == "INR"
        assert len(rec.key_advantages) >= 2
        assert any("Saves INR 2010" in adv for adv in rec.key_advantages)
        assert rec.is_strictly_better is True
