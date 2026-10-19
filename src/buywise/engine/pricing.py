"""Deterministic, currency-safe pricing arithmetic and distribution metrics."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Sequence

from buywise.engine.exceptions import (
    CurrencyMismatchError,
    InsufficientPriceDataError,
    InvalidPriceDataError,
)
from buywise.models.price import PriceMetrics, PriceSnapshot

CENT = Decimal("0.01")


def _quantize_currency(value: Decimal) -> Decimal:
    """Quantize decimal value to 2 decimal places using standard ROUND_HALF_UP."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_median(prices: Sequence[Decimal]) -> Decimal:
    """Calculate the exact median of a sequence of Decimal prices.
    
    Args:
        prices: Non-empty sequence of positive Decimal prices.
        
    Returns:
        Median value quantized to 2 decimal places.
        
    Raises:
        InsufficientPriceDataError: If prices sequence is empty.
    """
    if not prices:
        raise InsufficientPriceDataError("Cannot calculate median of an empty price series.")

    sorted_prices = sorted(prices)
    n = len(sorted_prices)
    mid = n // 2

    if n % 2 == 1:
        return _quantize_currency(sorted_prices[mid])
    else:
        avg = (sorted_prices[mid - 1] + sorted_prices[mid]) / Decimal("2")
        return _quantize_currency(avg)


def calculate_percentile_rank(
    current_price: Decimal, historical_prices: Sequence[Decimal]
) -> Decimal:
    """Calculate the percentile rank of the current price in historical distribution.
    
    A rank of 0.00% means the current price is strictly cheaper than all historical records.
    A rank of 100.00% means the current price is strictly higher than all historical records.
    Uses mid-count adjustment: (count_lower + 0.5 * count_equal) / N * 100.
    
    Args:
        current_price: The price being evaluated.
        historical_prices: Non-empty list of historical prices.
        
    Returns:
        Percentile rank between 0.00 and 100.00 quantized to 2 decimal places.
    """
    if not historical_prices:
        raise InsufficientPriceDataError("Historical prices list cannot be empty for percentile calculation.")

    n = Decimal(len(historical_prices))
    count_strictly_lower = Decimal(sum(1 for p in historical_prices if p < current_price))
    count_equal = Decimal(sum(1 for p in historical_prices if p == current_price))

    score = ((count_strictly_lower + (Decimal("0.5") * count_equal)) / n) * Decimal("100")
    # Clamp between 0 and 100
    if score < Decimal("0.0"):
        score = Decimal("0.0")
    elif score > Decimal("100.0"):
        score = Decimal("100.0")

    return _quantize_currency(score)


def compute_price_metrics(
    snapshots: Sequence[PriceSnapshot],
    current_price_override: Optional[Decimal] = None,
    reference_time: Optional[datetime] = None,
) -> PriceMetrics:
    """Compute deterministic price metrics across historical snapshots.
    
    Args:
        snapshots: Chronological or un-ordered sequence of PriceSnapshot records.
        current_price_override: Optional price override to evaluate against history.
        reference_time: Evaluation anchor time (defaults to newest snapshot timestamp).
        
    Returns:
        PriceMetrics with exact mathematical calculations.
        
    Raises:
        InsufficientPriceDataError: If snapshots is empty.
        CurrencyMismatchError: If snapshots contain mixed currencies.
        InvalidPriceDataError: If any price is <= 0.
    """
    if not snapshots:
        raise InsufficientPriceDataError("At least one price snapshot is required to compute metrics.")

    # 1. Currency validation - all snapshots must match currency
    currencies = {s.currency for s in snapshots}
    if len(currencies) > 1:
        raise CurrencyMismatchError(
            f"Mixed currencies detected in price history: {sorted(list(currencies))}. "
            "Cross-currency arithmetic is disallowed."
        )
    currency = next(iter(currencies))

    # 2. Check for invalid non-positive amounts
    for s in snapshots:
        if s.amount <= Decimal("0.0"):
            raise InvalidPriceDataError(
                f"Invalid non-positive price {s.amount} encountered for ASIN {s.asin} at {s.timestamp}."
            )

    asin = snapshots[0].asin

    # Sort snapshots by timestamp ascending
    sorted_snapshots = sorted(snapshots, key=lambda s: s.timestamp)
    latest_snapshot = sorted_snapshots[-1]

    # Reference time anchor
    anchor_time = reference_time or latest_snapshot.timestamp
    if anchor_time.tzinfo is None:
        anchor_time = anchor_time.replace(tzinfo=timezone.utc)

    # Determine current price
    if current_price_override is not None:
        if current_price_override <= Decimal("0.0"):
            raise InvalidPriceDataError(f"Current price override {current_price_override} must be positive.")
        current_price = _quantize_currency(current_price_override)
    else:
        current_price = _quantize_currency(latest_snapshot.amount)

    all_prices = [s.amount for s in sorted_snapshots]
    min_price = _quantize_currency(min(all_prices))
    max_price = _quantize_currency(max(all_prices))
    median_price = calculate_median(all_prices)
    percentile_rank = calculate_percentile_rank(current_price, all_prices)

    # 3. Rolling 30-day and 90-day medians
    cutoff_30d = anchor_time - timedelta(days=30)
    cutoff_90d = anchor_time - timedelta(days=90)

    prices_30d = [
        s.amount
        for s in sorted_snapshots
        if (s.timestamp.replace(tzinfo=timezone.utc) if s.timestamp.tzinfo is None else s.timestamp)
        >= cutoff_30d
    ]
    prices_90d = [
        s.amount
        for s in sorted_snapshots
        if (s.timestamp.replace(tzinfo=timezone.utc) if s.timestamp.tzinfo is None else s.timestamp)
        >= cutoff_90d
    ]

    rolling_30d_median = calculate_median(prices_30d) if prices_30d else None
    rolling_90d_median = calculate_median(prices_90d) if prices_90d else None

    # 4. Effective discount percentage calculated against 30-day median (or overall median)
    baseline_median = rolling_30d_median or median_price
    effective_discount_pct: Optional[Decimal] = None
    if baseline_median > Decimal("0.0"):
        diff = baseline_median - current_price
        discount_val = (diff / baseline_median) * Decimal("100")
        effective_discount_pct = _quantize_currency(discount_val)

    # 5. Artificial discount detection
    # If the listing claims a list_price (MSRP) that is significantly (>15%) higher
    # than the highest historical observed price in the last 90 days
    is_artificial_discount = False
    if latest_snapshot.list_price is not None and latest_snapshot.list_price > Decimal("0.0"):
        comp_max = max(prices_90d) if prices_90d else max_price
        if latest_snapshot.list_price > (comp_max * Decimal("1.15")):
            is_artificial_discount = True

    is_all_time_low = bool(current_price <= min_price)

    return PriceMetrics(
        asin=asin,
        currency=currency,
        sample_count=len(snapshots),
        current_price=current_price,
        min_price=min_price,
        max_price=max_price,
        median_price=median_price,
        percentile_rank=percentile_rank,
        rolling_30d_median=rolling_30d_median,
        rolling_90d_median=rolling_90d_median,
        effective_discount_pct=effective_discount_pct,
        is_artificial_discount=is_artificial_discount,
        is_all_time_low=is_all_time_low,
    )
