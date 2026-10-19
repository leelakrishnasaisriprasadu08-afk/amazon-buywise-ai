"""Pytest configuration and common test fixtures."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest

from buywise.models.identity import ProductIdentity
from buywise.models.price import PriceSnapshot, SellerType
from buywise.providers.mock_provider import MockFixtureProvider
from buywise.storage.sqlite_store import SQLiteAuditStore


@pytest.fixture
def mock_provider() -> MockFixtureProvider:
    """Fixture providing initialized MockFixtureProvider."""
    return MockFixtureProvider()


@pytest.fixture
def memory_store() -> SQLiteAuditStore:
    """Fixture providing in-memory SQLite audit repository."""
    return SQLiteAuditStore(db_path=":memory:")


@pytest.fixture
def sample_product() -> ProductIdentity:
    """Fixture providing a valid ProductIdentity instance."""
    return ProductIdentity(
        asin="B08N5WRWNW",
        marketplace="amazon.com",
        canonical_url="https://www.amazon.com/dp/B08N5WRWNW",
        title="Apple MacBook Air M1",
        brand="Apple",
        category="Computers",
    )


@pytest.fixture
def sample_price_snapshots() -> list[PriceSnapshot]:
    """Fixture providing a series of USD price snapshots."""
    base_time = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    return [
        PriceSnapshot(
            asin="B08N5WRWNW",
            timestamp=base_time.replace(day=1),
            currency="USD",
            amount=Decimal("899.00"),
            list_price=Decimal("999.00"),
            seller_type=SellerType.AMAZON_1P,
        ),
        PriceSnapshot(
            asin="B08N5WRWNW",
            timestamp=base_time.replace(day=5),
            currency="USD",
            amount=Decimal("849.00"),
            list_price=Decimal("999.00"),
            seller_type=SellerType.AMAZON_1P,
        ),
        PriceSnapshot(
            asin="B08N5WRWNW",
            timestamp=base_time.replace(day=10),
            currency="USD",
            amount=Decimal("749.00"),
            list_price=Decimal("999.00"),
            is_deal=True,
            seller_type=SellerType.AMAZON_1P,
        ),
    ]
