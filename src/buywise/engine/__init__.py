"""Deterministic engines and custom exceptions for BuyWise AI."""

from buywise.engine.exceptions import (
    BuyWiseError,
    CurrencyMismatchError,
    InsufficientPriceDataError,
    InvalidASINError,
    InvalidPriceDataError,
)
from buywise.engine.pricing import (
    calculate_median,
    calculate_percentile_rank,
    compute_price_metrics,
)
from buywise.engine.hybrid_retrieval import HybridReviewRetriever
from buywise.engine.aspect_analyzer import ReviewAspectAnalyzer
from buywise.engine.competitor_matcher import CompetitorComparisonEngine

__all__ = [
    "BuyWiseError",
    "CurrencyMismatchError",
    "InsufficientPriceDataError",
    "InvalidASINError",
    "InvalidPriceDataError",
    "calculate_median",
    "calculate_percentile_rank",
    "compute_price_metrics",
    "HybridReviewRetriever",
    "ReviewAspectAnalyzer",
    "CompetitorComparisonEngine",
]
