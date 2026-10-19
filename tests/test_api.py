"""Integration tests for FastAPI endpoints."""

from fastapi.testclient import TestClient
import pytest

from buywise.api.app import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test suite for HTTP API endpoints."""

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "BuyWise AI Foundation"
        assert data["version"] == "0.1.0"

    def test_parse_product_valid_url(self):
        payload = {"input_text": "https://www.amazon.com/Apple-MacBook-Air/dp/B08N5WRWNW"}
        response = client.post("/api/v1/parse-product", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["asin"] == "B08N5WRWNW"
        assert data["marketplace"] == "amazon.com"
        assert data["canonical_url"] == "https://www.amazon.com/dp/B08N5WRWNW"
        assert data["product"]["asin"] == "B08N5WRWNW"

    def test_parse_product_invalid_input(self):
        payload = {"input_text": "https://www.walmart.com/ip/12345"}
        response = client.post("/api/v1/parse-product", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "Unable to parse product" in data["detail"]

    def test_get_product_price_metrics_success(self):
        response = client.get("/api/v1/products/B08N5WRWNW/price-metrics?lookback_days=90")
        assert response.status_code == 200
        data = response.json()
        assert data["is_fixture"] is True
        assert data["source_type"] == "mock_fixture"
        assert data["source_url"].startswith("mock://fixture/prices/B08N5WRWNW")

        payload = data["payload"]
        assert payload["asin"] == "B08N5WRWNW"
        assert payload["currency"] == "USD"
        assert payload["current_price"] == "749.00"
        assert payload["is_all_time_low"] is True

    def test_get_product_price_metrics_unknown_asin(self):
        response = client.get("/api/v1/products/B0UNKNOWN99/price-metrics")
        assert response.status_code == 404
        data = response.json()
        assert "not found in fixture catalog" in data["detail"]

    def test_get_product_aspects_success(self):
        response = client.get("/api/v1/products/B08N5WRWNW/aspects")
        assert response.status_code == 200
        data = response.json()
        assert data["is_fixture"] is True
        payload = data["payload"]
        assert payload["asin"] == "B08N5WRWNW"
        assert payload["total_reviews_analyzed"] > 0
        assert "battery" in payload["aspects"]

    def test_get_product_alternatives_college_scenario(self):
        # Target is B0COLLEGE1 (VendorX), alternative auto-selected as B0COLLEGE2 (BenchmarkPro)
        response = client.get("/api/v1/products/B0COLLEGE1/alternatives")
        assert response.status_code == 200
        data = response.json()
        assert data["is_fixture"] is True
        payload = data["payload"]
        assert payload["target_asin"] == "B0COLLEGE1"
        assert payload["alternative_asin"] == "B0COLLEGE2"
        assert payload["price_delta"] == "2010.00"
        assert payload["is_strictly_better"] is True

    def test_analyze_product_sync_endpoint(self):
        payload = {"input_text": "B08N5WRWNW"}
        response = client.post("/api/v1/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["asin"] == "B08N5WRWNW"
        assert data["verdict"] == "BUY"
        assert data["confidence"] >= 0.85
        assert len(data["key_reasons"]) > 0

    def test_analyze_product_stream_endpoint(self):
        response = client.get("/api/v1/analyze/stream?input_text=B08N5WRWNW")
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        body_text = response.text
        assert "event: milestone" in body_text
        assert "event: complete" in body_text
        assert '"verdict": "BUY"' in body_text

    def test_search_products_endpoint(self):
        response = client.get("/api/v1/search?q=MacBook")
        assert response.status_code == 200
        items = response.json()
        assert len(items) >= 1
        assert any("MacBook" in p["title"] for p in items)
        assert items[0]["ai_verdict"] in ["BUY", "WAIT", "DONT_BUY", "INSUFFICIENT_EVIDENCE"]

    def test_list_all_products_endpoint(self):
        response = client.get("/api/v1/products")
        assert response.status_code == 200
        items = response.json()
        assert len(items) >= 6

    def test_get_product_card_endpoint(self):
        response = client.get("/api/v1/products/B08N5WRWNW/card")
        assert response.status_code == 200
        card = response.json()
        assert card["asin"] == "B08N5WRWNW"
        assert card["brand"] == "Apple"
        assert card["price"] == "749.00"

