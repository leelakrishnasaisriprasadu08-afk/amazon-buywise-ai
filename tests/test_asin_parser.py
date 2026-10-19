"""Comprehensive tests for deterministic ASIN and URL parsing."""

import pytest
from buywise.engine.exceptions import InvalidASINError
from buywise.parsers.asin import (
    build_canonical_url,
    create_product_identity,
    extract_marketplace_from_url,
    parse_asin_and_marketplace,
)


class TestASINParser:
    """Test suite for ASIN parsing, validation, and URL handling."""

    @pytest.mark.parametrize(
        "raw_input, expected_asin, expected_marketplace",
        [
            ("B08N5WRWNW", "B08N5WRWNW", "amazon.com"),
            ("b08n5wrwnw", "B08N5WRWNW", "amazon.com"),
            ("  B08N5WRWNW  ", "B08N5WRWNW", "amazon.com"),
            ("https://www.amazon.com/dp/B08N5WRWNW", "B08N5WRWNW", "amazon.com"),
            ("http://amazon.com/dp/B08N5WRWNW/", "B08N5WRWNW", "amazon.com"),
            (
                "https://www.amazon.com/Apple-MacBook-13-inch-256GB-Storage/dp/B08N5WRWNW",
                "B08N5WRWNW",
                "amazon.com",
            ),
            (
                "https://www.amazon.in/Apple-MacBook-13-inch-256GB/dp/B08N5WRWNW/ref=sr_1_1",
                "B08N5WRWNW",
                "amazon.in",
            ),
            (
                "https://www.amazon.co.uk/gp/product/B08N5WRWNW",
                "B08N5WRWNW",
                "amazon.co.uk",
            ),
            (
                "https://www.amazon.de/gp/product/glance/B08N5WRWNW",
                "B08N5WRWNW",
                "amazon.de",
            ),
            (
                "https://www.amazon.co.jp/product-reviews/B08N5WRWNW",
                "B08N5WRWNW",
                "amazon.co.jp",
            ),
            (
                "https://www.amazon.com/exec/obidos/ASIN/B08N5WRWNW/qid=123",
                "B08N5WRWNW",
                "amazon.com",
            ),
            (
                "https://www.amazon.com/gp/offer-listing/B08N5WRWNW",
                "B08N5WRWNW",
                "amazon.com",
            ),
            (
                "https://www.amazon.com/gp/aw/d/B08N5WRWNW",
                "B08N5WRWNW",
                "amazon.com",
            ),
            (
                "https://www.amazon.com/some-page?asin=B08N5WRWNW&tag=foo",
                "B08N5WRWNW",
                "amazon.com",
            ),
            (
                "www.amazon.com/dp/B08N5WRWNW",
                "B08N5WRWNW",
                "amazon.com",
            ),
        ],
    )
    def test_valid_asin_and_urls(self, raw_input: str, expected_asin: str, expected_marketplace: str):
        asin, marketplace = parse_asin_and_marketplace(raw_input)
        assert asin == expected_asin
        assert marketplace == expected_marketplace

    @pytest.mark.parametrize(
        "invalid_input",
        [
            "",
            "   ",
            "B08N5WRWN",        # 9 chars (too short)
            "B08N5WRWNWX",       # 11 chars (too long)
            "B08N5WR-NW",        # invalid hyphen
            "B08N5 WRNW",        # embedded space
            "https://www.walmart.com/ip/Apple-MacBook/1234567890",  # non-Amazon URL
            "https://www.ebay.com/itm/1234567890",                  # non-Amazon URL
            "https://www.amazon.com/gp/help/customer/display.html",  # Amazon URL without ASIN
            "not_an_asin_at_all",
        ],
    )
    def test_invalid_inputs_raise_error(self, invalid_input: str):
        with pytest.raises(InvalidASINError):
            parse_asin_and_marketplace(invalid_input)

    def test_non_string_input_raises_error(self):
        with pytest.raises(InvalidASINError):
            parse_asin_and_marketplace(None)  # type: ignore

        with pytest.raises(InvalidASINError):
            parse_asin_and_marketplace(1234567890)  # type: ignore

    def test_canonical_url_builder(self):
        url = build_canonical_url("B08N5WRWNW", "amazon.in")
        assert url == "https://www.amazon.in/dp/B08N5WRWNW"

    def test_create_product_identity(self):
        prod = create_product_identity(
            "https://www.amazon.com/dp/B08N5WRWNW",
            title="MacBook Air M1",
            brand="Apple",
        )
        assert prod.asin == "B08N5WRWNW"
        assert prod.marketplace == "amazon.com"
        assert prod.canonical_url == "https://www.amazon.com/dp/B08N5WRWNW"
        assert prod.title == "MacBook Air M1"
        assert prod.brand == "Apple"
