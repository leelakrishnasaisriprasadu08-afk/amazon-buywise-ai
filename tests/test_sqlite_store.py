"""Unit tests for SQLiteAuditStore persistence and Decimal precision."""

from datetime import datetime, timezone
from decimal import Decimal
from buywise.models.identity import ProductIdentity
from buywise.models.price import PriceSnapshot, SellerType
from buywise.models.provenance import ProvenanceEnvelope, SourceType
from buywise.models.report import DecisionVerdict, RecommendationReport
from buywise.storage.sqlite_store import SQLiteAuditStore


class TestSQLiteAuditStore:
    """Test suite for SQLite audit trail and exact Decimal persistence."""

    def test_product_save_and_retrieve(self, memory_store: SQLiteAuditStore):
        prod = ProductIdentity(
            asin="B08N5WRWNW",
            marketplace="amazon.com",
            canonical_url="https://www.amazon.com/dp/B08N5WRWNW",
            title="MacBook Air M1",
            brand="Apple",
            category="Laptops",
        )
        memory_store.save_product(prod)

        retrieved = memory_store.get_product("B08N5WRWNW")
        assert retrieved is not None
        assert retrieved.asin == "B08N5WRWNW"
        assert retrieved.title == "MacBook Air M1"
        assert retrieved.marketplace == "amazon.com"

    def test_price_snapshot_decimal_precision(self, memory_store: SQLiteAuditStore):
        now = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)
        snapshots = [
            PriceSnapshot(
                asin="B08N5WRWNW",
                timestamp=now,
                currency="USD",
                amount=Decimal("749.99"),
                list_price=Decimal("999.00"),
                is_deal=True,
                deal_type="Prime Day",
                seller_type=SellerType.AMAZON_1P,
            )
        ]
        memory_store.save_price_snapshots(snapshots)

        history = memory_store.get_price_history("B08N5WRWNW")
        assert len(history) == 1
        retrieved_snap = history[0]
        assert isinstance(retrieved_snap.amount, Decimal)
        assert retrieved_snap.amount == Decimal("749.99")
        assert retrieved_snap.list_price == Decimal("999.00")
        assert retrieved_snap.is_deal is True

    def test_evidence_envelope_audit(self, memory_store: SQLiteAuditStore):
        envelope = ProvenanceEnvelope[str](
            source_type=SourceType.MOCK_FIXTURE,
            source_url="mock://fixture/spec/B08N5WRWNW",
            confidence_score=1.0,
            is_fixture=True,
            payload="Apple M1 8-Core CPU",
        )
        memory_store.save_evidence_envelope(envelope)

    def test_recommendation_report_audit(self, memory_store: SQLiteAuditStore, sample_product: ProductIdentity):
        report = RecommendationReport(
            asin="B08N5WRWNW",
            verdict=DecisionVerdict.BUY,
            confidence=0.92,
            summary="Price at 90-day low with overwhelmingly positive verified reviews.",
            product=sample_product,
            key_reasons=["Price discount genuine", "High build quality satisfaction"],
        )
        audit_id = memory_store.save_recommendation_report(report)
        assert audit_id > 0
