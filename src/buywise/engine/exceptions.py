"""Custom domain exceptions for BuyWise engine operations."""


class BuyWiseError(Exception):
    """Base exception for all BuyWise domain errors."""


class InvalidASINError(BuyWiseError, ValueError):
    """Raised when an ASIN cannot be resolved, extracted, or validated."""


class CurrencyMismatchError(BuyWiseError, ValueError):
    """Raised when comparing or computing across different currencies."""


class InsufficientPriceDataError(BuyWiseError, ValueError):
    """Raised when price history observations are insufficient for metric calculations."""


class InvalidPriceDataError(BuyWiseError, ValueError):
    """Raised when encountering malformed or negative prices."""
