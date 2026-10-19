"""Domain contracts for currency-safe pricing snapshots and calculated metrics."""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SellerType(str, Enum):
    """Classification of the offer fulfillment / merchant."""

    AMAZON_1P = "amazon_1p"
    FBA_3P = "3p_fba"
    FBM_3P = "3p_fbm"
    UNKNOWN = "unknown"


CURRENCY_REGEX = re.compile(r"^[A-Z]{3}$")


class PriceSnapshot(BaseModel):
    """Point-in-time pricing record for an ASIN using exact Decimal arithmetic."""

    model_config = ConfigDict(frozen=True)

    asin: str = Field(description="10-character ASIN")
    timestamp: datetime = Field(description="Exact timestamp of observed price")
    currency: str = Field(description="3-letter ISO-4217 currency code (e.g. USD, EUR, GBP, INR)")
    amount: Decimal = Field(gt=Decimal("0.0"), description="Effective selling price")
    list_price: Optional[Decimal] = Field(
        default=None,
        gt=Decimal("0.0"),
        description="Declared MSRP or crossed-out reference price, if present",
    )
    is_deal: bool = Field(default=False, description="Whether marked as lightning deal / prime day deal")
    deal_type: Optional[str] = Field(default=None, description="Tag for deal promotion, if applicable")
    seller_type: SellerType = Field(default=SellerType.UNKNOWN, description="Fulfillment / seller classification")
    in_stock: bool = Field(default=True, description="Inventory availability at observation time")

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Currency code must be a string.")
        normalized = v.strip().upper()
        if not CURRENCY_REGEX.match(normalized):
            raise ValueError(f"Invalid currency code '{v}'. Must be 3 uppercase letters (e.g., USD, EUR).")
        return normalized

    @field_validator("amount", "list_price", mode="before")
    @classmethod
    def parse_decimal(cls, v: object) -> Optional[Decimal]:
        if v is None:
            return None
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        raise ValueError(f"Cannot cast {v} to Decimal.")


class PriceMetrics(BaseModel):
    """Deterministic, mathematically verified price intelligence metrics."""

    model_config = ConfigDict(frozen=True)

    asin: str = Field(description="10-character ASIN")
    currency: str = Field(description="3-letter ISO-4217 currency code for all values")
    sample_count: int = Field(ge=1, description="Number of historical pricing observations analyzed")
    current_price: Decimal = Field(description="Most recent observed price")
    min_price: Decimal = Field(description="All-time low observed within window")
    max_price: Decimal = Field(description="All-time high observed within window")
    median_price: Decimal = Field(description="Historical median price")
    percentile_rank: Decimal = Field(
        ge=Decimal("0.0"),
        le=Decimal("100.0"),
        description="Percentile position of current price (0.0 = lowest, 100.0 = highest)",
    )
    rolling_30d_median: Optional[Decimal] = Field(
        default=None,
        description="Median price within the trailing 30 days, if records exist",
    )
    rolling_90d_median: Optional[Decimal] = Field(
        default=None,
        description="Median price within the trailing 90 days, if records exist",
    )
    effective_discount_pct: Optional[Decimal] = Field(
        default=None,
        description="True discount percentage computed against 30-day baseline median",
    )
    is_artificial_discount: bool = Field(
        default=False,
        description="True if list price was inflated above recent max right before sale",
    )
    is_all_time_low: bool = Field(
        default=False,
        description="True if current price is at or below historical min",
    )
    computed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC calculation timestamp",
    )
