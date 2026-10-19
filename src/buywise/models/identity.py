"""Domain contract for product identity and canonical metadata."""

from datetime import datetime, timezone
import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


ASIN_REGEX = re.compile(r"^[A-Z0-9]{10}$")


class ProductIdentity(BaseModel):
    """Canonical representation of an Amazon product."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    asin: str = Field(description="10-character alphanumeric Amazon Standard Identification Number")
    marketplace: str = Field(default="amazon.com", description="Canonical domain/marketplace, e.g. amazon.com, amazon.in")
    canonical_url: str = Field(description="Standardized canonical URL for the product")
    title: Optional[str] = Field(default=None, description="Product title, if resolved")
    brand: Optional[str] = Field(default=None, description="Product brand name, if resolved")
    category: Optional[str] = Field(default=None, description="Primary catalog category, if resolved")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when identity record was initialized",
    )

    @field_validator("asin", mode="before")
    @classmethod
    def validate_and_normalize_asin(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError(f"ASIN must be a string, got {type(v).__name__}")
        normalized = v.strip().upper()
        if not ASIN_REGEX.match(normalized):
            raise ValueError(f"Invalid ASIN '{v}'. Must be exactly 10 alphanumeric characters.")
        return normalized

    @field_validator("marketplace", mode="before")
    @classmethod
    def normalize_marketplace(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError(f"Marketplace must be a string, got {type(v).__name__}")
        cleaned = v.strip().lower()
        if not cleaned:
            return "amazon.com"
        # Strip protocol if accidentally included
        cleaned = re.sub(r"^https?://", "", cleaned)
        cleaned = re.sub(r"^www\.", "", cleaned)
        cleaned = cleaned.split("/")[0]
        return cleaned
