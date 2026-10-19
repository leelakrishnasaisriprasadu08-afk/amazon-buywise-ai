"""Domain contracts for head-to-head product comparisons and alternative recommendations."""

from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class FeatureDelta(BaseModel):
    """Specific spec or capability difference between target and alternative product."""

    model_config = ConfigDict(frozen=True)

    feature_name: str = Field(description="Name of the attribute (e.g., RAM, Display, Battery)")
    target_value: str = Field(description="Specification of the product being evaluated")
    alternative_value: str = Field(description="Specification of the competitor product")
    advantage: str = Field(
        description="Which product has the clear advantage ('alternative', 'target', or 'neutral')"
    )
    impact_summary: str = Field(description="Explanation of why this difference matters to the buyer")


class AlternativeRecommendation(BaseModel):
    """Evidence-backed alternative product recommendation."""

    model_config = ConfigDict(frozen=True)

    target_asin: str = Field(description="Original product ASIN")
    alternative_asin: str = Field(description="Recommended alternative ASIN")
    alternative_title: str = Field(description="Title of the alternative product")
    target_price: Decimal = Field(description="Current effective price of target product")
    alternative_price: Decimal = Field(description="Current effective price of alternative product")
    price_delta: Decimal = Field(
        description="target_price - alternative_price (positive value means alternative is cheaper)"
    )
    currency: str = Field(description="Currency code for both prices")
    key_advantages: List[str] = Field(
        default_factory=list,
        description="Top advantages of switching to the alternative",
    )
    trade_offs: List[str] = Field(
        default_factory=list,
        description="Minor trade-offs or shortcomings of the alternative",
    )
    feature_deltas: List[FeatureDelta] = Field(
        default_factory=list,
        description="Detailed feature-by-feature comparison matrix",
    )
    is_strictly_better: bool = Field(
        default=False,
        description="True if alternative is equal or cheaper while superior on critical specs",
    )
