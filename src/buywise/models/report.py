"""Domain contract for recommendation reports with transparent missing evidence tracking."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from buywise.models.aspect import ProductAspectAnalysis
from buywise.models.comparison import AlternativeRecommendation
from buywise.models.identity import ProductIdentity
from buywise.models.price import PriceMetrics
from buywise.models.provenance import ProvenanceEnvelope


class DecisionVerdict(str, Enum):
    """The four core decision outcomes of BuyWise AI."""

    BUY = "BUY"
    WAIT = "WAIT"
    DONT_BUY = "DONT_BUY"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class RecommendationReport(BaseModel):
    """Evidence-grounded recommendation report with complete provenance and auditability."""

    model_config = ConfigDict(frozen=True)

    asin: str = Field(description="Target 10-character ASIN")
    verdict: DecisionVerdict = Field(description="Primary recommendation outcome")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall decision confidence based strictly on evidence completeness",
    )
    summary: str = Field(description="Evidence-grounded explanation of the recommendation")
    product: ProductIdentity = Field(description="Canonical product identity")
    price_metrics: Optional[PriceMetrics] = Field(
        default=None,
        description="Deterministic pricing intelligence, if historical records exist",
    )
    aspect_analysis: Optional[ProductAspectAnalysis] = Field(
        default=None,
        description="Review aspect breakdown and grounded citations, if reviews exist",
    )
    alternative: Optional[AlternativeRecommendation] = Field(
        default=None,
        description="Candidate competitor alternative comparison, if evaluated",
    )
    evidence_envelopes: List[ProvenanceEnvelope[Any]] = Field(
        default_factory=list,
        description="Verifiable source envelopes supporting the recommendation",
    )
    key_reasons: List[str] = Field(
        default_factory=list,
        description="Core factors driving the verdict (e.g. price at 90d low, verified reviews)",
    )
    risks_and_caveats: List[str] = Field(
        default_factory=list,
        description="Documented product shortcomings and trade-offs",
    )
    missing_evidence: List[str] = Field(
        default_factory=list,
        description="Explicitly listed gaps (e.g., lack of verified reviews, missing price history)",
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when report was synthesized",
    )
