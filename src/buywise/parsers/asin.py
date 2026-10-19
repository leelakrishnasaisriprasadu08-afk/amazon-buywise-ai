"""Deterministic parser and extractor for Amazon ASINs and URLs."""

import re
from typing import Optional, Tuple
from urllib.parse import parse_qs, urlparse

from buywise.engine.exceptions import InvalidASINError
from buywise.models.identity import ProductIdentity

# Regex matching a valid 10-character Amazon Standard Identification Number
ASIN_STRICT_REGEX = re.compile(r"^[A-Z0-9]{10}$")

# Regexes matching URL paths containing ASIN
URL_ASIN_PATTERNS = [
    re.compile(r"/dp/([A-Za-z0-9]{10})", re.IGNORECASE),
    re.compile(r"/gp/product/(?:glance/)?([A-Za-z0-9]{10})", re.IGNORECASE),
    re.compile(r"/gp/aw/d/([A-Za-z0-9]{10})", re.IGNORECASE),
    re.compile(r"/d/([A-Za-z0-9]{10})", re.IGNORECASE),
    re.compile(r"/product-reviews/([A-Za-z0-9]{10})", re.IGNORECASE),
    re.compile(r"/exec/obidos/ASIN/([A-Za-z0-9]{10})", re.IGNORECASE),
    re.compile(r"/o/ASIN/([A-Za-z0-9]{10})", re.IGNORECASE),
    re.compile(r"/gp/offer-listing/([A-Za-z0-9]{10})", re.IGNORECASE),
]

# Supported / recognized Amazon domain suffix pattern
AMAZON_HOST_REGEX = re.compile(r"^(?:[a-zA-Z0-9-]+\.)*amazon\.(com|in|co\.uk|de|ca|co\.jp|com\.au|es|fr|it|nl|sg|ae|sa|se|pl|com\.br|com\.mx)$", re.IGNORECASE)


def extract_marketplace_from_url(url: str) -> str:
    """Extract and normalize canonical Amazon marketplace domain from a URL.
    
    Defaults to 'amazon.com' if not explicitly determinable.
    """
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return "amazon.com"
        
        # Remove www. or m. prefix
        cleaned = re.sub(r"^(www\.|m\.)", "", hostname)
        if AMAZON_HOST_REGEX.match(cleaned):
            return cleaned
        elif "amazon." in cleaned:
            # Fallback for regional Amazon domains
            return cleaned
        raise InvalidASINError(f"URL hostname '{hostname}' is not a recognized Amazon marketplace.")
    except Exception as e:
        if isinstance(e, InvalidASINError):
            raise
        return "amazon.com"


def parse_asin_and_marketplace(input_str: str) -> Tuple[str, str]:
    """Deterministically parse an ASIN and marketplace from either a raw ASIN or an Amazon URL.

    Args:
        input_str: Raw ASIN (e.g. 'B08N5WRWNW') or full Amazon product URL.

    Returns:
        Tuple of (canonical_asin, canonical_marketplace)

    Raises:
        InvalidASINError: If input is empty, malformed, non-Amazon, or contains no extractable ASIN.
    """
    if not input_str or not isinstance(input_str, str):
        raise InvalidASINError("Input must be a non-empty string.")

    cleaned = input_str.strip()
    if not cleaned:
        raise InvalidASINError("Input cannot be blank or whitespace-only.")

    # 1. Check if raw input is directly an ASIN
    upper_cleaned = cleaned.upper()
    if ASIN_STRICT_REGEX.match(upper_cleaned):
        return upper_cleaned, "amazon.com"

    # 2. Check if input is a URL
    if cleaned.startswith(("http://", "https://", "www.", "amazon.")):
        normalized_url = cleaned
        if not normalized_url.startswith(("http://", "https://")):
            normalized_url = f"https://{normalized_url}"

        try:
            parsed = urlparse(normalized_url)
        except Exception as exc:
            raise InvalidASINError(f"Malformed URL string: {cleaned}") from exc

        marketplace = extract_marketplace_from_url(normalized_url)

        # Check path patterns
        path = parsed.path
        for pattern in URL_ASIN_PATTERNS:
            match = pattern.search(path)
            if match:
                extracted_asin = match.group(1).upper()
                if ASIN_STRICT_REGEX.match(extracted_asin):
                    return extracted_asin, marketplace

        # Check query parameters (e.g., ?asin=B08N5WRWNW)
        query_params = parse_qs(parsed.query)
        if "asin" in query_params and query_params["asin"]:
            cand = query_params["asin"][0].strip().upper()
            if ASIN_STRICT_REGEX.match(cand):
                return cand, marketplace

        if "ASIN" in query_params and query_params["ASIN"]:
            cand = query_params["ASIN"][0].strip().upper()
            if ASIN_STRICT_REGEX.match(cand):
                return cand, marketplace

        raise InvalidASINError(f"Could not locate a valid 10-character ASIN in URL: {cleaned}")

    # 3. If neither a valid direct ASIN nor a recognizable URL
    raise InvalidASINError(
        f"Invalid input '{cleaned}'. Must be a 10-character alphanumeric ASIN or a valid Amazon URL."
    )


def build_canonical_url(asin: str, marketplace: str = "amazon.com") -> str:
    """Build standard canonical Amazon URL for an ASIN and marketplace."""
    return f"https://www.{marketplace}/dp/{asin}"


def create_product_identity(
    input_str: str,
    title: Optional[str] = None,
    brand: Optional[str] = None,
    category: Optional[str] = None,
) -> ProductIdentity:
    """Parse input and construct a validated ProductIdentity instance."""
    asin, marketplace = parse_asin_and_marketplace(input_str)
    canonical_url = build_canonical_url(asin, marketplace)
    return ProductIdentity(
        asin=asin,
        marketplace=marketplace,
        canonical_url=canonical_url,
        title=title,
        brand=brand,
        category=category,
    )
