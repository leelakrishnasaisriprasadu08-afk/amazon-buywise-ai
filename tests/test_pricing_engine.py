"""Unit tests for deterministic pricing calculations, median, percentiles, and currency safety."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest

from buywise.engine.exceptions import (
    CurrencyMismatchError,
    InsufficientPriceDataError,
    InvalidPriceDataError,
)
from buywise.engine.pricing import (
    calculate_median,
    calculate_percentile_rank,
    compute_price_metrics,
)
from buywise.models.price import PriceSnapshot, SellerType


class TestPricingCalculations:
    """Test suite for exact Decimal median, percentile rank, and currency arithmetic."""

    def test_median_odd_elements(self):
        prices = [Decimal("10.00"), Decimal("50.00"), Decimal("30.00")]
        assert calculate_median(prices) == Decimal("30.00")

    def test_median_even_elements(self):
        prices = [Decimal("10.00"), Decimal("20.00"), Decimal("30.00"), Decimal("40.00")]
        assert calculate_median(prices) == Decimal("25.00")

    def test_median_single_element(self):
        prices = [Decimal("99.99")]
        assert calculate_median(prices) == Decimal("99.99")

    def test_median_empty_raises_error(self):
        with pytest.raises(InsufficientPriceDataError):
            calculate_median([])

    def test_percentile_rank_extremes(self):
        history = [Decimal("100.00"), Decimal("200.00"), Decimal("300.00"), Decimal("400.00")]
        # Cheaper than all historical
        rank_cheaper = calculate_percentile_rank(Decimal("50.00"), history)
        assert rank_cheaper == Decimal("0.00")

        # More expensive than all historical
        rank_expensive = calculate_percentile_rank(Decimal("500.00"), history)
        assert rank_expensive == Decimal("100.00")

        # Equal to lowest item (100.00): (0 + 0.5 * 1)/4 * 100 = 12.50
        rank_lowest = calculate_percentile_rank(Decimal("100.00"), history)
        assert rank_lowest == Decimal("12.50")

    def test_percentile_rank_empty_raises_error(self):
        with pytest.raises(InsufficientPriceDataError):
            calculate_percentile_rank(Decimal("100.00"), [])


class TestComputePriceMetrics:
    """Test suite for compute_price_metrics engine function."""

    @pytest.fixture
    def anchor_time(self) -> datetime:
        return datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)

    def test_standard_metrics_computation(self, anchor_time: datetime):
        snapshots = [
            PriceSnapshot(
                asin="B08N5WRWNW",
                timestamp=anchor_time - timedelta(days=60),
                currency="USD",
                amount=Decimal("899.00"),
                list_price=Decimal("999.00"),
            ),
            PriceSnapshot(
                asin="B08N5WRWNW",
                timestamp=anchor_time - timedelta(days=20),
                currency="USD",
                amount=Decimal("849.00"),
                list_price=Decimal("999.00"),
            ),
            PriceSnapshot(
                asin="B08N5WRWNW",
                timestamp=anchor_time,
                currency="USD",
                amount=Decimal("749.00"),
                list_price=Decimal("999.00"),
                is_deal=True,
            ),
        ]

        metrics = compute_price_metrics(snapshots, reference_time=anchor_time)

        assert metrics.asin == "B08N5WRWNW"
        assert metrics.currency == "USD"
        assert metrics.sample_count == 3
        assert metrics.current_price == Decimal("749.00")
        assert metrics.min_price == Decimal("749.00")
        assert metrics.max_price == Decimal("899.00")
        assert metrics.median_price == Decimal("849.00")
        assert metrics.is_all_time_low is True
        assert metrics.rolling_30d_median == Decimal("799.00")  # (849 + 749) / 2
        assert metrics.rolling_90d_median == Decimal("849.00")
        assert metrics.effective_discount_pct is not None
        assert metrics.is_artificial_discount is False

    def test_single_snapshot_metrics(self, anchor_time: datetime):
        snapshots = [
            PriceSnapshot(
                asin="B0NEWITEM0",
                timestamp=anchor_time,
                currency="USD",
                amount=Decimal("19.99"),
                list_price=Decimal("19.99"),
            )
        ]
        metrics = compute_price_metrics(snapshots, reference_time=anchor_time)
        assert metrics.sample_count == 1
        assert metrics.current_price == Decimal("19.99")
        assert metrics.median_price == Decimal("19.99")
        assert metrics.min_price == Decimal("19.99")
        assert metrics.max_price == Decimal("19.99")
        assert metrics.is_all_time_low is True
        assert metrics.percentile_rank == Decimal("50.00")

    def test_empty_snapshots_raises_insufficient_data(self):
        with pytest.raises(InsufficientPriceDataError):
            compute_price_metrics([])

    def test_currency_mismatch_raises_error(self, anchor_time: datetime):
        snapshots = [
            PriceSnapshot(
                asin="B08N5WRWNW",
                timestamp=anchor_time - timedelta(days=2),
                currency="USD",
                amount=Decimal("100.00"),
            ),
            PriceSnapshot(
                asin="B08N5WRWNW",
                timestamp=anchor_time,
                currency="EUR",  # Mixed currency!
                amount=Decimal("95.00"),
            ),
        ]
        with pytest.raises(CurrencyMismatchError) as exc_info:
            compute_price_metrics(snapshots)
        assert "Mixed currencies detected" in str(exc_info.value)

    def test_zero_or_negative_price_raises_error(self, anchor_time: datetime):
        # We can construct snapshot with bypass or model validator
        with pytest.raises(ValueError):
            PriceSnapshot(
                asin="B08N5WRWNW",
                timestamp=anchor_time,
                currency="USD",
                amount=Decimal("-10.00"),
            )

    def test_artificial_discount_detection(self, anchor_time: datetime):
        # Historical prices between $100 and $120.
        # Current list price claimed is $200 (way above 120 * 1.15 = 138), with "sale" at $115
        snapshots = [
            PriceSnapshot(
                asin="B0FAKE999",
                timestamp=anchor_time - timedelta(days=40),
                currency="USD",
                amount=Decimal("100.00"),
                list_price=Decimal("110.00"),
            ),
            PriceSnapshot(
                asin="B0FAKE999",
                timestamp=anchor_time - timedelta(days=20),
                currency="USD",
                amount=Decimal("120.00"),
                list_price=Decimal("120.00"),
            ),
            PriceSnapshot(
                asin="B0FAKE999",
                timestamp=anchor_time,
                currency="USD",
                amount=Decimal("115.00"),
                list_price=Decimal("200.00"),  # Inflated list price!
                is_deal=True,
            ),
        ]
        metrics = compute_price_metrics(snapshots, reference_time=anchor_time)
        assert metrics.is_artificial_discount is True

    def test_current_price_override(self, anchor_time: datetime):
        snapshots = [
            PriceSnapshot(
                asin="B08N5WRWNW",
                timestamp=anchor_time - timedelta(days=1),
                currency="USD",
                amount=Decimal("100.00"),
            )
        ]
        metrics = compute_price_metrics(
            snapshots, current_price_override=Decimal("80.00"), reference_time=anchor_time
        )
        assert metrics.current_price == Decimal("80.00")
        assert metrics.is_all_time_low is True
        assert metrics.percentile_rank == Decimal("0.00")
