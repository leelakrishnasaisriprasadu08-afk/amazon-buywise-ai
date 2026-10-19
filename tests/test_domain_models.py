"""Unit tests for domain model contracts, immutability, and validation rules."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest
from pydantic import ValidationError

from buywise.models.identity import ProductIdentity
from buywise.models.price import PriceMetrics, PriceSnapshot, SellerType
from buywise.models.provenance import ProvenanceEnvelope, SourceType
from buywise.models.report import DecisionVerdict, RecommendationReport
from buywise.models.review import ReviewRecord


class TestDomainModels:
    """Test suite for domain model constraints and honesty invariants."""

    def test_product_identity_immutability(self):
        prod = ProductIdentity(
            asin="B08N5WRWNW",
            marketplace="amazon.com",
            canonical_url="https://www.amazon.com/dp/B08N5WRWNW",
            title="MacBook Air M1",
        )
        with pytest.raises(ValidationError):
            prod.title = "Modified Title"  # type: ignore

    def test_product_identity_invalid_asin(self):
        with pytest.raises(ValidationError):
            ProductIdentity(
                asin="INVALID",
                marketplace="amazon.com",
                canonical_url="https://www.amazon.com/dp/INVALID",
            )

    def test_provenance_envelope_mock_fixture_honesty(self):
        # MOCK_FIXTURE with is_fixture=False MUST fail validation
        with pytest.raises(ValidationError) as exc:
            ProvenanceEnvelope[str](
                source_type=SourceType.MOCK_FIXTURE,
                source_url="mock://fixture/test",
                confidence_score=1.0,
                is_fixture=False,  # Violation!
                payload="sample",
            )
        assert "SourceType.MOCK_FIXTURE must explicitly have is_fixture=True" in str(exc.value)

    def test_provenance_envelope_live_source_cannot_claim_fixture(self):
        # AMAZON_CATALOG with is_fixture=True MUST fail validation
        with pytest.raises(ValidationError) as exc:
            ProvenanceEnvelope[str](
                source_type=SourceType.AMAZON_CATALOG,
                source_url="https://api.amazon.com/catalog",
                confidence_score=0.9,
                is_fixture=True,  # Inconsistent!
                payload="sample",
            )
        assert "cannot have live source_type" in str(exc.value)

    def test_review_record_rating_boundaries(self):
        now = datetime.now(timezone.utc)
        # Valid rating
        rev = ReviewRecord(
            review_id="REV-1",
            asin="B08N5WRWNW",
            rating=Decimal("4.5"),
            title="Great",
            body="Worked well",
            review_date=now,
            is_verified_purchase=True,
        )
        assert rev.rating == Decimal("4.5")

        # Rating too high (> 5.0)
        with pytest.raises(ValidationError):
            ReviewRecord(
                review_id="REV-2",
                asin="B08N5WRWNW",
                rating=Decimal("5.5"),
                title="Invalid",
                body="Invalid",
                review_date=now,
            )

        # Rating too low (< 1.0)
        with pytest.raises(ValidationError):
            ReviewRecord(
                review_id="REV-3",
                asin="B08N5WRWNW",
                rating=Decimal("0.5"),
                title="Invalid",
                body="Invalid",
                review_date=now,
            )

    def test_price_snapshot_currency_normalization(self):
        now = datetime.now(timezone.utc)
        snap = PriceSnapshot(
            asin="B08N5WRWNW",
            timestamp=now,
            currency="usd",  # lowercase should normalize to uppercase
            amount=Decimal("99.99"),
        )
        assert snap.currency == "USD"

        # Invalid currency code (e.g. 2 letters)
        with pytest.raises(ValidationError):
            PriceSnapshot(
                asin="B08N5WRWNW",
                timestamp=now,
                currency="US",
                amount=Decimal("99.99"),
            )

    def test_recommendation_report_missing_evidence_tracking(self):
        now = datetime.now(timezone.utc)
        prod = ProductIdentity(
            asin="B0NEWITEM0",
            marketplace="amazon.com",
            canonical_url="https://www.amazon.com/dp/B0NEWITEM0",
        )
        report = RecommendationReport(
            asin="B0NEWITEM0",
            verdict=DecisionVerdict.INSUFFICIENT_EVIDENCE,
            confidence=0.3,
            summary="Item listed 3 days ago. No historical price depth or verified reviews.",
            product=prod,
            missing_evidence=[
                "verified_reviews_count_below_threshold (1 < 5)",
                "historical_pricing_duration_below_threshold (1d < 14d)",
            ],
        )
        assert report.verdict == DecisionVerdict.INSUFFICIENT_EVIDENCE
        assert len(report.missing_evidence) == 2
        assert "verified_reviews_count_below_threshold" in report.missing_evidence[0]
