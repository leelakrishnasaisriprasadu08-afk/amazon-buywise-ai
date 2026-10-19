"""Tests for OpenWebNinja Real-Time Amazon Data Provider."""

from decimal import Decimal
import pytest
from buywise.providers.realtime_amazon import (
    RealtimeAmazonProvider,
    _clean_price_string,
    _extract_brand,
)


class TestRealtimeAmazonProvider:
    """Security and resilience test suite for RealtimeAmazonProvider."""

    def test_masked_key_security(self):
        """Verify the raw API key is never exposed in logs or diagnostics."""
        provider = RealtimeAmazonProvider(api_key="ak_g9y1zoq965c2a9mxl3l0hazvukb19pm8i9qy9046ixalpvr")
        masked = provider.masked_key
        assert "ak_g9y" in masked
        assert "pvr" in masked
        assert "zoq965c2a9mxl3l0hazvukb19pm8i9qy9046ixa" not in masked
        assert masked == "ak_g9y...lpvr"

    def test_unconfigured_masked_key(self):
        """Verify behavior when no API key is provided."""
        provider = RealtimeAmazonProvider(api_key="")
        assert provider.masked_key == "NOT_CONFIGURED"
        assert provider.is_configured is False

    def test_clean_price_string(self):
        """Verify regex numeric price parsing across multiple currencies."""
        assert _clean_price_string("$162.49") == Decimal("162.49")
        assert _clean_price_string("₹52,490.00") == Decimal("52490.00")
        assert _clean_price_string("EUR 89.95") == Decimal("89.95")
        assert _clean_price_string(None) is None
        assert _clean_price_string("FREE") is None

    def test_extract_brand(self):
        """Verify heuristic brand identification."""
        assert _extract_brand("Samsung Galaxy S24 Ultra") == "Samsung"
        assert _extract_brand("Apple MacBook Air M2 13.6-inch") == "Apple"
        assert _extract_brand("Sony WH-1000XM5 Wireless Headphones") == "Sony"
        assert _extract_brand("Ergonomic Wireless Mouse with USB") == "Ergonomic"

    def test_empty_query_returns_empty_list(self):
        """Verify whitespace/empty queries return immediately without network call."""
        provider = RealtimeAmazonProvider(api_key="ak_dummy_test_key_12345")
        results = provider.search_products("   ")
        assert results == []
