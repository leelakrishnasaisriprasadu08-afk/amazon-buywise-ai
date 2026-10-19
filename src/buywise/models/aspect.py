"""Domain contracts for review aspect extraction, citations, and defect forensics."""

from datetime import datetime
from enum import Enum
from typing import Dict, List
from pydantic import BaseModel, ConfigDict, Field


class AspectCategory(str, Enum):
    """Core evaluation dimensions for product quality and longevity."""

    BATTERY = "battery"
    BUILD_QUALITY = "build_quality"
    DISPLAY = "display"
    PERFORMANCE = "performance"
    VALUE = "value"
    USABILITY = "usability"
    DEFECT = "defect"


class SentimentPolarity(str, Enum):
    """Sentiment classification for aspect mentions."""

    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


class AspectCitation(BaseModel):
    """Verbatim citation linking an aspect claim directly to a verified customer review."""

    model_config = ConfigDict(frozen=True)

    review_id: str = Field(description="Originating review identifier")
    quote: str = Field(description="Exact excerpt from the customer review body")
    is_verified_purchase: bool = Field(description="Whether the reviewer has a verified purchase badge")
    review_date: datetime = Field(description="When the review was posted")
    helpful_votes: int = Field(ge=0, description="Helpful votes count for this review")


class AspectSummary(BaseModel):
    """Aggregated sentiment and grounded citations for a single product aspect."""

    model_config = ConfigDict(frozen=True)

    category: AspectCategory = Field(description="Aspect category name")
    sentiment: SentimentPolarity = Field(description="Overall aspect sentiment polarity")
    positive_mentions: int = Field(ge=0, default=0)
    negative_mentions: int = Field(ge=0, default=0)
    total_mentions: int = Field(ge=0, default=0)
    satisfaction_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Weighted satisfaction score (0.0 = terrible, 1.0 = flawless)",
    )
    citations: List[AspectCitation] = Field(
        default_factory=list,
        description="Verbatim citations supporting this aspect evaluation",
    )
    top_defect_keywords: List[str] = Field(
        default_factory=list,
        description="Specific recurring complaint terms identified in negative citations",
    )


class ProductAspectAnalysis(BaseModel):
    """Full grounded review forensics report for a product."""

    model_config = ConfigDict(frozen=True)

    asin: str = Field(description="Target 10-character ASIN")
    total_reviews_analyzed: int = Field(ge=0)
    verified_review_ratio: float = Field(
        ge=0.0,
        le=1.0,
        description="Proportion of analyzed reviews from verified purchasers",
    )
    aspects: Dict[AspectCategory, AspectSummary] = Field(
        default_factory=dict,
        description="Evaluated aspect summaries",
    )
    critical_defects: List[str] = Field(
        default_factory=list,
        description="Highlighted recurring hardware or functional failure patterns",
    )
    defect_rate: float = Field(
        ge=0.0,
        le=1.0,
        description="Percentage of analyzed reviews reporting recurring defects or failures",
    )
