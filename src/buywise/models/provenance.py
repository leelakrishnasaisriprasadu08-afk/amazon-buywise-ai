"""Domain contract for strict evidence provenance tracking."""

from datetime import datetime, timezone
from enum import Enum
from typing import Generic, Optional, TypeVar
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field, model_validator


T = TypeVar("T")


class SourceType(str, Enum):
    """Enumeration of recognized data source providers."""

    AMAZON_CATALOG = "amazon_catalog"
    MOCK_FIXTURE = "mock_fixture"
    KEEPA_API = "keepa_api"
    RAINFOREST_API = "rainforest_api"
    EDITORIAL_REVIEW = "editorial_review"
    USER_SUBMISSION = "user_submission"


class ProvenanceEnvelope(BaseModel, Generic[T]):
    """Cryptographically verifiable envelope tracking source and veracity of evidence."""

    model_config = ConfigDict(frozen=True)

    evidence_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Globally unique identifier for this evidence item",
    )
    source_type: SourceType = Field(description="Originating source classification")
    source_url: str = Field(description="Exact URL or locator URI from which data was retrieved")
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp at retrieval time",
    )
    raw_hash_sha256: Optional[str] = Field(
        default=None,
        description="SHA-256 digest of raw payload bytes to ensure immutability",
    )
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Authority/integrity score between 0.0 and 1.0",
    )
    is_verified_source: bool = Field(
        default=True,
        description="Whether data stems from a cryptographically or officially verified endpoint",
    )
    is_fixture: bool = Field(
        default=False,
        description="Explicit flag: MUST be True if source is a mock/fixture, NEVER masquerades as live data",
    )
    payload: T = Field(description="Structured evidence payload")

    @model_validator(mode="after")
    def validate_fixture_honesty(self) -> "ProvenanceEnvelope[T]":
        """Enforce transparency: mock fixtures can never claim to be live sources."""
        if self.source_type == SourceType.MOCK_FIXTURE and not self.is_fixture:
            raise ValueError(
                "SourceType.MOCK_FIXTURE must explicitly have is_fixture=True to guarantee transparency."
            )
        if self.is_fixture and self.source_type != SourceType.MOCK_FIXTURE:
            raise ValueError(
                f"Item marked is_fixture=True cannot have live source_type '{self.source_type}'."
            )
        return self
