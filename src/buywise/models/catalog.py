"""Domain contract for Amazon Catalog Products and search results."""

from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from buywise.models.report import DecisionVerdict


class CatalogProduct(BaseModel):
    """Rich product representation for Amazon catalog browsing and search results."""

    model_config = ConfigDict(frozen=True)

    asin: str = Field(description="10-character Amazon ASIN")
    title: str = Field(description="Full product title")
    brand: str = Field(description="Brand or manufacturer")
    category: str = Field(description="Product category, e.g. Laptops, Smartphones, Audio")
    price: Decimal = Field(description="Current selling price")
    list_price: Decimal = Field(description="Original list price / MSRP")
    currency: str = Field(default="USD", description="Currency symbol or ISO code")
    rating: Decimal = Field(description="Average Amazon star rating (1.0 to 5.0)")
    review_count: int = Field(description="Total count of customer reviews")
    image_url: str = Field(description="Product image URL or SVG identifier")
    prime: bool = Field(default=True, description="Prime 1-day/2-day shipping eligibility")
    deal_badge: Optional[str] = Field(default=None, description="E.g. 'Limited time deal', 'Prime Big Deal', '25% off'")
    ai_verdict: DecisionVerdict = Field(description="BuyWise AI verdict outcome")
    ai_verdict_summary: str = Field(description="Short human-readable summary of AI verdict")
    specs: List[str] = Field(default_factory=list, description="Key hardware specifications")
    marketplace: str = Field(default="amazon.com", description="Marketplace domain")
    is_fixture: bool = Field(default=True, description="Whether data is sourced from golden fixture")
