"""Unit tests for MockFixtureProvider and transparency guarantees."""

import pytest
from buywise.engine.exceptions import InvalidASINError
from buywise.models.provenance import SourceType
from buywise.providers.mock_provider import MockFixtureProvider
from buywise.providers.protocols import (
    PriceHistoryProvider,
    ProductCatalogProvider,
    ReviewProvider,
)


class TestMockFixtureProvider:
    """Test suite ensuring MockFixtureProvider honesty and protocol compliance."""

    def test_protocol_conformance(self, mock_provider: MockFixtureProvider):
        assert isinstance(mock_provider, ProductCatalogProvider)
        assert isinstance(mock_provider, PriceHistoryProvider)
        assert isinstance(mock_provider, ReviewProvider)

    @pytest.mark.parametrize("asin", ["B08N5WRWNW", "B09V3K3EXP", "B07DEFECT0", "B0NEWITEM0"])
    def test_fixture_honesty_and_provenance(self, mock_provider: MockFixtureProvider, asin: str):
        envelope = mock_provider.get_product(asin)

        # Transparency asserts
        assert envelope.source_type == SourceType.MOCK_FIXTURE
        assert envelope.is_fixture is True
        assert envelope.is_verified_source is False  # Must never claim to be live external API
        assert envelope.source_url.startswith("mock://fixture/catalog/")
        assert envelope.confidence_score == 1.0
        assert envelope.raw_hash_sha256 is not None
        assert envelope.payload.asin == asin

    def test_get_product_unknown_asin_raises_error(self, mock_provider: MockFixtureProvider):
        with pytest.raises(InvalidASINError):
            mock_provider.get_product("B0UNKNOWN99")

    def test_get_price_history(self, mock_provider: MockFixtureProvider):
        envelope = mock_provider.get_price_history("B08N5WRWNW", lookback_days=30)
        assert envelope.is_fixture is True
        assert len(envelope.payload) > 0
        assert all(s.asin == "B08N5WRWNW" for s in envelope.payload)
        assert all(s.currency == "USD" for s in envelope.payload)

    def test_get_reviews_pagination_limit(self, mock_provider: MockFixtureProvider):
        envelope = mock_provider.get_reviews("B08N5WRWNW", limit=2)
        assert envelope.is_fixture is True
        assert len(envelope.payload) == 2
        assert envelope.payload[0].review_id.startswith("REV-M1-")
