"""BuyWise domain models and typed contracts."""

from buywise.models.identity import ProductIdentity
from buywise.models.provenance import ProvenanceEnvelope, SourceType
from buywise.models.review import ReviewRecord
from buywise.models.price import PriceSnapshot, PriceMetrics, SellerType
from buywise.models.report import RecommendationReport, DecisionVerdict
from buywise.models.aspect import (
    AspectCategory,
    SentimentPolarity,
    AspectCitation,
    AspectSummary,
    ProductAspectAnalysis,
)
from buywise.models.comparison import FeatureDelta, AlternativeRecommendation

__all__ = [
    "ProductIdentity",
    "ProvenanceEnvelope",
    "SourceType",
    "ReviewRecord",
    "PriceSnapshot",
    "PriceMetrics",
    "SellerType",
    "RecommendationReport",
    "DecisionVerdict",
    "AspectCategory",
    "SentimentPolarity",
    "AspectCitation",
    "AspectSummary",
    "ProductAspectAnalysis",
    "FeatureDelta",
    "AlternativeRecommendation",
]
