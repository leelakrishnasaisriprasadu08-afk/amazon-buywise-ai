"""Abstract provider protocols defining interfaces for catalog, pricing, and reviews."""

from typing import List, Protocol, runtime_checkable
from buywise.models.identity import ProductIdentity
from buywise.models.price import PriceSnapshot
from buywise.models.provenance import ProvenanceEnvelope
from buywise.models.review import ReviewRecord


@runtime_checkable
class ProductCatalogProvider(Protocol):
    """Protocol for fetching verified canonical product identity and specs."""

    def get_product(self, asin: str, marketplace: str = "amazon.com") -> ProvenanceEnvelope[ProductIdentity]:
        """Fetch canonical product identity enveloped with provenance."""
        ...


@runtime_checkable
class PriceHistoryProvider(Protocol):
    """Protocol for fetching time-series price snapshots."""

    def get_price_history(
        self, asin: str, marketplace: str = "amazon.com", lookback_days: int = 90
    ) -> ProvenanceEnvelope[List[PriceSnapshot]]:
        """Fetch historical price snapshots enveloped with provenance."""
        ...


@runtime_checkable
class ReviewProvider(Protocol):
    """Protocol for fetching customer reviews."""

    def get_reviews(
        self, asin: str, marketplace: str = "amazon.com", limit: int = 100
    ) -> ProvenanceEnvelope[List[ReviewRecord]]:
        """Fetch review records enveloped with provenance."""
        ...
