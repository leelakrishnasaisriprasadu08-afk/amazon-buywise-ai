"""Domain contract for verified customer reviews and metadata."""

from datetime import datetime
from decimal import Decimal
import re
from typing import List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReviewRecord(BaseModel):
    """Normalized review record preserving verified badges, timestamps, and helpful votes."""

    model_config = ConfigDict(frozen=True)

    review_id: str = Field(description="Unique review identifier from platform")
    asin: str = Field(description="Associated 10-character ASIN")
    rating: Decimal = Field(
        ge=Decimal("1.0"),
        le=Decimal("5.0"),
        description="Rating score between 1.0 and 5.0",
    )
    title: str = Field(description="Headline or title of the review")
    body: str = Field(description="Full text content of the review")
    review_date: datetime = Field(description="Date and time review was posted")
    is_verified_purchase: bool = Field(
        default=False,
        description="Explicit badge indicating verified Amazon customer purchase",
    )
    helpful_votes: int = Field(
        default=0,
        ge=0,
        description="Count of helpful votes by other shoppers",
    )
    aspect_tags: List[str] = Field(
        default_factory=list,
        description="Aspect categories tagged in downstream processing",
    )

    @field_validator("asin", mode="before")
    @classmethod
    def validate_asin(cls, v: str) -> str:
        if not isinstance(v, str) or not re.match(r"^[A-Za-z0-9]{10}$", v.strip()):
            raise ValueError(f"Invalid ASIN '{v}' for review.")
        return v.strip().upper()

    @field_validator("rating", mode="before")
    @classmethod
    def validate_rating_decimal(cls, v: object) -> Decimal:
        if isinstance(v, (int, float, str)):
            dec = Decimal(str(v))
            if dec < Decimal("1.0") or dec > Decimal("5.0"):
                raise ValueError(f"Rating {v} must be between 1.0 and 5.0.")
            return dec
        elif isinstance(v, Decimal):
            if v < Decimal("1.0") or v > Decimal("5.0"):
                raise ValueError(f"Rating {v} must be between 1.0 and 5.0.")
            return v
        raise ValueError(f"Cannot convert rating {v} to Decimal.")
