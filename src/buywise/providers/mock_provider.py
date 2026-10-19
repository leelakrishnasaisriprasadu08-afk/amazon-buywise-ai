"""Explicitly labeled Mock Fixture Provider for testing and offline development.

CRITICAL POLICY:
This provider strictly serves recorded golden fixtures. All data returned
is explicitly marked with `source_type=SourceType.MOCK_FIXTURE` and `is_fixture=True`.
It NEVER masquerades as live Amazon data.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import re
from typing import Dict, List, Optional

from buywise.engine.exceptions import InvalidASINError
from buywise.models.catalog import CatalogProduct
from buywise.models.identity import ProductIdentity
from buywise.models.price import PriceSnapshot, SellerType
from buywise.models.provenance import ProvenanceEnvelope, SourceType
from buywise.models.report import DecisionVerdict
from buywise.models.review import ReviewRecord
from buywise.parsers.asin import build_canonical_url, parse_asin_and_marketplace
from buywise.providers.protocols import (
    PriceHistoryProvider,
    ProductCatalogProvider,
    ReviewProvider,
)

# Reference anchor time for deterministic fixture generation (2026-10-10 UTC)
MOCK_NOW = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)


def _compute_sha256(content: str) -> str:
    """Deterministic SHA-256 hash calculation."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class MockFixtureProvider(ProductCatalogProvider, PriceHistoryProvider, ReviewProvider):
    """In-memory golden fixture provider with full provenance envelope and strict honesty flags."""

    def __init__(self) -> None:
        self._catalogs: Dict[str, ProductIdentity] = {}
        self._catalog_cards: Dict[str, CatalogProduct] = {}
        self._price_histories: Dict[str, List[PriceSnapshot]] = {}
        self._reviews: Dict[str, List[ReviewRecord]] = {}
        self._load_fixtures()

    def _load_fixtures(self) -> None:
        """Seed rich, realistic golden fixtures covering primary domain edge cases and full Amazon product catalog."""

        # -------------------------------------------------------------
        # FIXTURE 1: B08N5WRWNW - Apple MacBook Air M1 (Genuine Deal at near all-time low)
        # -------------------------------------------------------------
        asin_1 = "B08N5WRWNW"
        self._catalogs[asin_1] = ProductIdentity(
            asin=asin_1,
            marketplace="amazon.com",
            canonical_url=build_canonical_url(asin_1, "amazon.com"),
            title="Apple MacBook Air 13.3-inch Laptop - M1 Chip, 8GB RAM, 256GB SSD Storage - Space Gray",
            brand="Apple",
            category="Laptops & MacBooks",
            created_at=MOCK_NOW - timedelta(days=365),
        )
        self._catalog_cards[asin_1] = CatalogProduct(
            asin=asin_1,
            title="Apple MacBook Air 13.3-inch Laptop - M1 Chip, 8GB RAM, 256GB SSD Storage - Space Gray",
            brand="Apple",
            category="Laptops & MacBooks",
            price=Decimal("749.00"),
            list_price=Decimal("999.00"),
            currency="USD",
            rating=Decimal("4.8"),
            review_count=18492,
            image_url="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="Prime Big Deal • 25% Off",
            ai_verdict=DecisionVerdict.BUY,
            ai_verdict_summary="Verified All-Time Low ($749 vs $899 90d median). 0% critical defect rate.",
            specs=["Apple M1 8-Core CPU", "8GB Unified Memory", "256GB SSD", "Retina Display", "18hr Battery"],
            marketplace="amazon.com",
            is_fixture=True,
        )
        history_1: List[PriceSnapshot] = []
        for day in range(90, 0, -1):
            ts = MOCK_NOW - timedelta(days=day)
            price_amt = Decimal("749.00") if day <= 10 else (Decimal("899.00") if day % 5 != 0 else Decimal("849.00"))
            history_1.append(
                PriceSnapshot(
                    asin=asin_1,
                    timestamp=ts,
                    currency="USD",
                    amount=price_amt,
                    list_price=Decimal("999.00"),
                    is_deal=(day <= 10),
                    deal_type="Prime Big Deal" if day <= 10 else None,
                    seller_type=SellerType.AMAZON_1P,
                    in_stock=True,
                )
            )
        self._price_histories[asin_1] = history_1
        self._reviews[asin_1] = [
            ReviewRecord(
                review_id="REV-M1-001",
                asin=asin_1,
                rating=Decimal("5.0"),
                title="Astonishing battery life and completely silent",
                body="The M1 chip is unbelievable. Battery easily lasts 15+ hours of web browsing and video editing. No fan noise whatsoever.",
                review_date=MOCK_NOW - timedelta(days=45),
                is_verified_purchase=True,
                helpful_votes=142,
                aspect_tags=["battery", "performance", "build_quality"],
            ),
            ReviewRecord(
                review_id="REV-M1-002",
                asin=asin_1,
                rating=Decimal("4.0"),
                title="Great machine but 8GB RAM has limits",
                body="Build quality and screen are top tier. If you have 50 chrome tabs and heavy Docker containers, you might feel memory pressure.",
                review_date=MOCK_NOW - timedelta(days=20),
                is_verified_purchase=True,
                helpful_votes=58,
                aspect_tags=["performance", "value"],
            ),
            ReviewRecord(
                review_id="REV-M1-003",
                asin=asin_1,
                rating=Decimal("5.0"),
                title="Unbeatable value at $749",
                body="Keyboard is comfortable and trackpad is the best in the industry. Outstanding buy at this discounted price.",
                review_date=MOCK_NOW - timedelta(days=5),
                is_verified_purchase=True,
                helpful_votes=29,
                aspect_tags=["value", "usability"],
            ),
        ]

        # -------------------------------------------------------------
        # FIXTURE 2: B09V3K3EXP - Apex Ultra 5G Smartphone (Artificial Pre-Sale Discount)
        # -------------------------------------------------------------
        asin_2 = "B09V3K3EXP"
        self._catalogs[asin_2] = ProductIdentity(
            asin=asin_2,
            marketplace="amazon.com",
            canonical_url=build_canonical_url(asin_2, "amazon.com"),
            title="Apex Ultra 5G Smartphone - 120Hz OLED, 256GB Storage, AI Quad Camera - Phantom Black",
            brand="Apex",
            category="Smartphones & Tablets",
            created_at=MOCK_NOW - timedelta(days=180),
        )
        self._catalog_cards[asin_2] = CatalogProduct(
            asin=asin_2,
            title="Apex Ultra 5G Smartphone - 120Hz OLED, 256GB Storage, AI Quad Camera - Phantom Black",
            brand="Apex",
            category="Smartphones & Tablets",
            price=Decimal("899.00"),
            list_price=Decimal("1299.00"),
            currency="USD",
            rating=Decimal("3.9"),
            review_count=3420,
            image_url="https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="Lightning Deal • Claimed 31% Off",
            ai_verdict=DecisionVerdict.WAIT,
            ai_verdict_summary="Artificial MSRP Markup. True price was $849 last week; currently $50 above median.",
            specs=["6.7\" 120Hz AMOLED", "256GB UFS 4.0", "50MP AI Quad", "5000mAh Battery", "65W Charging"],
            marketplace="amazon.com",
            is_fixture=True,
        )
        history_2: List[PriceSnapshot] = []
        for day in range(60, 0, -1):
            ts = MOCK_NOW - timedelta(days=day)
            history_2.append(
                PriceSnapshot(
                    asin=asin_2,
                    timestamp=ts,
                    currency="USD",
                    amount=Decimal("849.00") if day > 3 else Decimal("899.00"),
                    list_price=Decimal("1299.00") if day <= 3 else Decimal("899.00"),
                    is_deal=(day <= 3),
                    deal_type="Lightning Deal" if day <= 3 else None,
                    seller_type=SellerType.FBA_3P,
                    in_stock=True,
                )
            )
        self._price_histories[asin_2] = history_2
        self._reviews[asin_2] = [
            ReviewRecord(
                review_id="REV-APX-001",
                asin=asin_2,
                rating=Decimal("4.0"),
                title="Good screen but battery life is just average",
                body="Display is beautiful and fast. However camera software has lag in low light.",
                review_date=MOCK_NOW - timedelta(days=15),
                is_verified_purchase=True,
                helpful_votes=12,
                aspect_tags=["display", "battery"],
            )
        ]

        # -------------------------------------------------------------
        # FIXTURE 3: B07DEFECT0 - TurboClick Mechanical Mouse (High rating with recurrent defect)
        # -------------------------------------------------------------
        asin_3 = "B07DEFECT0"
        self._catalogs[asin_3] = ProductIdentity(
            asin=asin_3,
            marketplace="amazon.com",
            canonical_url=build_canonical_url(asin_3, "amazon.com"),
            title="TurboClick Ergonomic Pro Gaming Mouse - 26K DPI Optical Sensor, 8 Programmable Buttons",
            brand="TurboClick",
            category="Gaming & PC",
            created_at=MOCK_NOW - timedelta(days=120),
        )
        self._catalog_cards[asin_3] = CatalogProduct(
            asin=asin_3,
            title="TurboClick Ergonomic Pro Gaming Mouse - 26K DPI Optical Sensor, 8 Programmable Buttons",
            brand="TurboClick",
            category="Gaming & PC",
            price=Decimal("49.99"),
            list_price=Decimal("59.99"),
            currency="USD",
            rating=Decimal("4.4"),
            review_count=8720,
            image_url="https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="Best Seller in PC Gaming",
            ai_verdict=DecisionVerdict.DONT_BUY,
            ai_verdict_summary="Recurrent Hardware Defect: 38% cluster of scroll-wheel and double-click failures within 60 days.",
            specs=["26K DPI Optical", "8 Programmable Keys", "RGB Lighting", "Braided Speed Cable"],
            marketplace="amazon.com",
            is_fixture=True,
        )
        self._price_histories[asin_3] = [
            PriceSnapshot(
                asin=asin_3,
                timestamp=MOCK_NOW - timedelta(days=d),
                currency="USD",
                amount=Decimal("49.99"),
                list_price=Decimal("59.99"),
                is_deal=False,
                seller_type=SellerType.AMAZON_1P,
                in_stock=True,
            )
            for d in range(30, 0, -1)
        ]
        self._reviews[asin_3] = [
            ReviewRecord(
                review_id="REV-TC-001",
                asin=asin_3,
                rating=Decimal("1.0"),
                title="Scroll wheel broke within 6 weeks",
                body="Sensor stopped registering downward scrolls after 45 days. Exact same issue happened to my replacement.",
                review_date=MOCK_NOW - timedelta(days=12),
                is_verified_purchase=True,
                helpful_votes=88,
                aspect_tags=["build_quality", "defect"],
            ),
            ReviewRecord(
                review_id="REV-TC-002",
                asin=asin_3,
                rating=Decimal("2.0"),
                title="Double click issue makes it unusable",
                body="Left click began double clicking intermittently after two months of regular office use.",
                review_date=MOCK_NOW - timedelta(days=8),
                is_verified_purchase=True,
                helpful_votes=43,
                aspect_tags=["build_quality", "defect"],
            ),
        ]

        # -------------------------------------------------------------
        # FIXTURE 4: B0NEWITEM0 - SuperSpeed 7-Port USB Hub (Insufficient Data)
        # -------------------------------------------------------------
        asin_4 = "B0NEWITEM0"
        self._catalogs[asin_4] = ProductIdentity(
            asin=asin_4,
            marketplace="amazon.com",
            canonical_url=build_canonical_url(asin_4, "amazon.com"),
            title="SuperSpeed 7-Port USB 3.2 Gen 2 Compact Hub - 10Gbps High Transfer Aluminum Enclosure",
            brand="GenericTech",
            category="Tech Accessories",
            created_at=MOCK_NOW - timedelta(days=3),
        )
        self._catalog_cards[asin_4] = CatalogProduct(
            asin=asin_4,
            title="SuperSpeed 7-Port USB 3.2 Gen 2 Compact Hub - 10Gbps High Transfer Aluminum Enclosure",
            brand="GenericTech",
            category="Tech Accessories",
            price=Decimal("19.99"),
            list_price=Decimal("19.99"),
            currency="USD",
            rating=Decimal("5.0"),
            review_count=1,
            image_url="https://images.unsplash.com/photo-1544652478-6653e09f18a2?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="New Release",
            ai_verdict=DecisionVerdict.INSUFFICIENT_EVIDENCE,
            ai_verdict_summary="Insufficient Evidence: Brand new listing (3 days old) with only 1 unverified review.",
            specs=["7x USB 3.2 Ports", "10Gbps Data Rate", "Aluminum Shielding", "Plug & Play"],
            marketplace="amazon.com",
            is_fixture=True,
        )
        self._price_histories[asin_4] = [
            PriceSnapshot(
                asin=asin_4,
                timestamp=MOCK_NOW - timedelta(days=1),
                currency="USD",
                amount=Decimal("19.99"),
                list_price=Decimal("19.99"),
                is_deal=False,
                seller_type=SellerType.FBM_3P,
                in_stock=True,
            )
        ]
        self._reviews[asin_4] = [
            ReviewRecord(
                review_id="REV-NEW-001",
                asin=asin_4,
                rating=Decimal("5.0"),
                title="Works great",
                body="Plugged in and it worked.",
                review_date=MOCK_NOW - timedelta(days=1),
                is_verified_purchase=False,
                helpful_votes=0,
                aspect_tags=[],
            )
        ]

        # -------------------------------------------------------------
        # FIXTURE 5: B0COLLEGE1 - VendorX SlimBook 14 (Soldered RAM, Fake Discount, TN screen)
        # -------------------------------------------------------------
        asin_5 = "B0COLLEGE1"
        self._catalogs[asin_5] = ProductIdentity(
            asin=asin_5,
            marketplace="amazon.in",
            canonical_url=build_canonical_url(asin_5, "amazon.in"),
            title="VendorX SlimBook 14 - Intel Core i5 12th Gen, 8GB Soldered RAM, 512GB SSD, 14-inch FHD TN",
            brand="VendorX",
            category="Laptops & MacBooks",
            created_at=MOCK_NOW - timedelta(days=200),
        )
        self._catalog_cards[asin_5] = CatalogProduct(
            asin=asin_5,
            title="VendorX SlimBook 14 - Intel Core i5 12th Gen, 8GB Soldered RAM, 512GB SSD, 14-inch FHD TN",
            brand="VendorX",
            category="Laptops & MacBooks",
            price=Decimal("52000.00"),
            list_price=Decimal("68000.00"),
            currency="INR",
            rating=Decimal("3.8"),
            review_count=1240,
            image_url="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="Great Indian Festival • 24% Off",
            ai_verdict=DecisionVerdict.DONT_BUY,
            ai_verdict_summary="Switch Recommended: 8GB soldered RAM bottleneck & TN display. BenchmarkPro 14 is ₹2,010 cheaper with 16GB RAM + IPS.",
            specs=["Intel Core i5-1235U", "8GB Soldered RAM (0 slots)", "512GB SSD", "14\" TN 250nits", "1.4kg"],
            marketplace="amazon.in",
            is_fixture=True,
        )
        self._price_histories[asin_5] = [
            PriceSnapshot(
                asin=asin_5,
                timestamp=MOCK_NOW - timedelta(days=d),
                currency="INR",
                amount=Decimal("52000.00"),
                list_price=Decimal("68000.00"),
                is_deal=(d <= 5),
                deal_type="Lightning Deal" if d <= 5 else None,
                seller_type=SellerType.FBA_3P,
                in_stock=True,
            )
            for d in range(60, 0, -1)
        ]
        self._reviews[asin_5] = [
            ReviewRecord(
                review_id="REV-VX-001",
                asin=asin_5,
                rating=Decimal("2.0"),
                title="8GB soldered RAM is a huge mistake for college",
                body="Slows down heavily when running Zoom alongside 15 Chrome tabs. The memory is soldered with zero slots to upgrade. Huge lag and stutter.",
                review_date=MOCK_NOW - timedelta(days=25),
                is_verified_purchase=True,
                helpful_votes=74,
                aspect_tags=["performance", "defect"],
            ),
            ReviewRecord(
                review_id="REV-VX-002",
                asin=asin_5,
                rating=Decimal("2.0"),
                title="Screen viewing angles are washed out",
                body="The 250 nits TN screen has poor contrast and washed out colors. Difficult to read in bright lecture halls.",
                review_date=MOCK_NOW - timedelta(days=18),
                is_verified_purchase=True,
                helpful_votes=31,
                aspect_tags=["display"],
            ),
        ]

        # -------------------------------------------------------------
        # FIXTURE 6: B0COLLEGE2 - BenchmarkPro 14 (16GB RAM, IPS screen, Genuine Deal)
        # -------------------------------------------------------------
        asin_6 = "B0COLLEGE2"
        self._catalogs[asin_6] = ProductIdentity(
            asin=asin_6,
            marketplace="amazon.in",
            canonical_url=build_canonical_url(asin_6, "amazon.in"),
            title="BenchmarkPro 14 - AMD Ryzen 5 7530U, 16GB RAM, 512GB SSD, 14-inch IPS 300 nits Anti-Glare",
            brand="BenchmarkPro",
            category="Laptops & MacBooks",
            created_at=MOCK_NOW - timedelta(days=150),
        )
        self._catalog_cards[asin_6] = CatalogProduct(
            asin=asin_6,
            title="BenchmarkPro 14 - AMD Ryzen 5 7530U, 16GB RAM, 512GB SSD, 14-inch IPS 300 nits Anti-Glare",
            brand="BenchmarkPro",
            category="Laptops & MacBooks",
            price=Decimal("49990.00"),
            list_price=Decimal("54990.00"),
            currency="INR",
            rating=Decimal("4.6"),
            review_count=3890,
            image_url="https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="Amazon's Choice",
            ai_verdict=DecisionVerdict.BUY,
            ai_verdict_summary="Superior Alternative: Saves ₹2,010, includes 16GB dual-channel RAM and 300-nit IPS screen.",
            specs=["AMD Ryzen 5 7530U", "16GB Dual Channel RAM", "512GB NVMe SSD", "14\" IPS 300nits", "8hr Battery"],
            marketplace="amazon.in",
            is_fixture=True,
        )
        self._price_histories[asin_6] = [
            PriceSnapshot(
                asin=asin_6,
                timestamp=MOCK_NOW - timedelta(days=d),
                currency="INR",
                amount=Decimal("49990.00"),
                list_price=Decimal("54990.00"),
                is_deal=True,
                seller_type=SellerType.AMAZON_1P,
                in_stock=True,
            )
            for d in range(60, 0, -1)
        ]
        self._reviews[asin_6] = [
            ReviewRecord(
                review_id="REV-BP-001",
                asin=asin_6,
                rating=Decimal("5.0"),
                title="Outstanding laptop for engineering students",
                body="The 16GB dual channel RAM handles programming and multi-tasking effortlessly. Fast and silent performance with 8 hours of battery.",
                review_date=MOCK_NOW - timedelta(days=14),
                is_verified_purchase=True,
                helpful_votes=95,
                aspect_tags=["performance", "battery"],
            ),
            ReviewRecord(
                review_id="REV-BP-002",
                asin=asin_6,
                rating=Decimal("5.0"),
                title="Bright IPS screen is wonderful for long study hours",
                body="Crisp 300 nits IPS display with wide angles. Sturdy metal lid and great typing comfort.",
                review_date=MOCK_NOW - timedelta(days=10),
                is_verified_purchase=True,
                helpful_votes=42,
                aspect_tags=["display", "build_quality"],
            ),
        ]

        # -------------------------------------------------------------
        # FIXTURE 7: B09XS7JWHH - Sony WH-1000XM5 Wireless Noise Canceling Headphones
        # -------------------------------------------------------------
        asin_7 = "B09XS7JWHH"
        self._catalogs[asin_7] = ProductIdentity(
            asin=asin_7,
            marketplace="amazon.com",
            canonical_url=build_canonical_url(asin_7, "amazon.com"),
            title="Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones - Black",
            brand="Sony",
            category="Audio & Headphones",
            created_at=MOCK_NOW - timedelta(days=300),
        )
        self._catalog_cards[asin_7] = CatalogProduct(
            asin=asin_7,
            title="Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones - Black",
            brand="Sony",
            category="Audio & Headphones",
            price=Decimal("328.00"),
            list_price=Decimal("399.99"),
            currency="USD",
            rating=Decimal("4.7"),
            review_count=14820,
            image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="Save 18% • Lowest Price in 30 Days",
            ai_verdict=DecisionVerdict.BUY,
            ai_verdict_summary="Genuine 18% Discount at 90-day percentile rank 12%. 96% positive ANC and battery sentiment.",
            specs=["Auto NC Optimizer", "30hr Battery Life", "8 Microphones with AI", "Multipoint Connection"],
            marketplace="amazon.com",
            is_fixture=True,
        )
        self._price_histories[asin_7] = [
            PriceSnapshot(
                asin=asin_7,
                timestamp=MOCK_NOW - timedelta(days=d),
                currency="USD",
                amount=Decimal("328.00") if d <= 14 else Decimal("398.00"),
                list_price=Decimal("399.99"),
                is_deal=(d <= 14),
                seller_type=SellerType.AMAZON_1P,
                in_stock=True,
            )
            for d in range(90, 0, -1)
        ]
        self._reviews[asin_7] = [
            ReviewRecord(
                review_id="REV-SNY-001",
                asin=asin_7,
                rating=Decimal("5.0"),
                title="The gold standard for office and flight noise cancellation",
                body="Airplane cabin drone completely vanishes. Call clarity is crystal clear and battery lasts multiple days on a single charge.",
                review_date=MOCK_NOW - timedelta(days=20),
                is_verified_purchase=True,
                helpful_votes=110,
                aspect_tags=["battery", "performance", "build_quality"],
            ),
            ReviewRecord(
                review_id="REV-SNY-002",
                asin=asin_7,
                rating=Decimal("5.0"),
                title="Plush earcups and superb soundstage",
                body="Much lighter than AirPods Max. Earcups do not cause ear fatigue even after 6 straight hours of Zoom calls.",
                review_date=MOCK_NOW - timedelta(days=12),
                is_verified_purchase=True,
                helpful_votes=48,
                aspect_tags=["usability", "performance"],
            ),
        ]

        # -------------------------------------------------------------
        # FIXTURE 8: B0CHWRXH8B - Apple AirPods Pro (2nd Generation) USB-C
        # -------------------------------------------------------------
        asin_8 = "B0CHWRXH8B"
        self._catalogs[asin_8] = ProductIdentity(
            asin=asin_8,
            marketplace="amazon.com",
            canonical_url=build_canonical_url(asin_8, "amazon.com"),
            title="Apple AirPods Pro (2nd Gen) Wireless Earbuds with MagSafe Case (USB-C) - White",
            brand="Apple",
            category="Audio & Headphones",
            created_at=MOCK_NOW - timedelta(days=220),
        )
        self._catalog_cards[asin_8] = CatalogProduct(
            asin=asin_8,
            title="Apple AirPods Pro (2nd Gen) Wireless Earbuds with MagSafe Case (USB-C) - White",
            brand="Apple",
            category="Audio & Headphones",
            price=Decimal("189.99"),
            list_price=Decimal("249.00"),
            currency="USD",
            rating=Decimal("4.8"),
            review_count=23400,
            image_url="https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="Limited Time Deal • 24% Off",
            ai_verdict=DecisionVerdict.BUY,
            ai_verdict_summary="Verified Deal at All-Time Low ($189.99 vs $239 median). Top-rated transparency and ANC.",
            specs=["Apple H2 Chip", "2x Active Noise Cancellation", "Adaptive Audio", "USB-C MagSafe Case", "IP54 Dust & Water"],
            marketplace="amazon.com",
            is_fixture=True,
        )
        self._price_histories[asin_8] = [
            PriceSnapshot(
                asin=asin_8,
                timestamp=MOCK_NOW - timedelta(days=d),
                currency="USD",
                amount=Decimal("189.99") if d <= 7 else Decimal("239.00"),
                list_price=Decimal("249.00"),
                is_deal=(d <= 7),
                seller_type=SellerType.AMAZON_1P,
                in_stock=True,
            )
            for d in range(60, 0, -1)
        ]
        self._reviews[asin_8] = [
            ReviewRecord(
                review_id="REV-APP-001",
                asin=asin_8,
                rating=Decimal("5.0"),
                title="USB-C upgrade and phenomenal noise cancellation",
                body="Adaptive transparency mode is witchcraft. Switching seamlessly between iPhone and Mac makes everyday life wonderful.",
                review_date=MOCK_NOW - timedelta(days=15),
                is_verified_purchase=True,
                helpful_votes=85,
                aspect_tags=["performance", "usability"],
            )
        ]

        # -------------------------------------------------------------
        # FIXTURE 9: B09HM94VDS - Logitech MX Master 3S Wireless Mouse
        # -------------------------------------------------------------
        asin_9 = "B09HM94VDS"
        self._catalogs[asin_9] = ProductIdentity(
            asin=asin_9,
            marketplace="amazon.com",
            canonical_url=build_canonical_url(asin_9, "amazon.com"),
            title="Logitech MX Master 3S Performance Wireless Mouse - Quiet Clicks, 8K DPI Sensor - Graphite",
            brand="Logitech",
            category="Gaming & PC",
            created_at=MOCK_NOW - timedelta(days=280),
        )
        self._catalog_cards[asin_9] = CatalogProduct(
            asin=asin_9,
            title="Logitech MX Master 3S Performance Wireless Mouse - Quiet Clicks, 8K DPI Sensor - Graphite",
            brand="Logitech",
            category="Gaming & PC",
            price=Decimal("99.99"),
            list_price=Decimal("99.99"),
            currency="USD",
            rating=Decimal("4.7"),
            review_count=19200,
            image_url="https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="Amazon's Choice in Computer Mice",
            ai_verdict=DecisionVerdict.BUY,
            ai_verdict_summary="Extremely Low Defect Rate (<1.2%). Superior MagSpeed electromagnetic scroll mechanism.",
            specs=["8000 DPI Darkfield Sensor", "Quiet Click 90% Noise Reduction", "MagSpeed Scroll Wheel", "70-day Battery"],
            marketplace="amazon.com",
            is_fixture=True,
        )
        self._price_histories[asin_9] = [
            PriceSnapshot(
                asin=asin_9,
                timestamp=MOCK_NOW - timedelta(days=d),
                currency="USD",
                amount=Decimal("99.99"),
                list_price=Decimal("99.99"),
                is_deal=False,
                seller_type=SellerType.AMAZON_1P,
                in_stock=True,
            )
            for d in range(60, 0, -1)
        ]
        self._reviews[asin_9] = [
            ReviewRecord(
                review_id="REV-LOGI-001",
                asin=asin_9,
                rating=Decimal("5.0"),
                title="The best mouse on the planet for productivity",
                body="The MagSpeed wheel scrolls through 1000 lines of code per second silently. Ergonomics have cured my wrist pain.",
                review_date=MOCK_NOW - timedelta(days=30),
                is_verified_purchase=True,
                helpful_votes=140,
                aspect_tags=["usability", "build_quality"],
            )
        ]

        # -------------------------------------------------------------
        # FIXTURE 10: B0CRDFABCD - Samsung Galaxy S24 Ultra 5G
        # -------------------------------------------------------------
        asin_10 = "B0CRDFABCD"
        self._catalogs[asin_10] = ProductIdentity(
            asin=asin_10,
            marketplace="amazon.com",
            canonical_url=build_canonical_url(asin_10, "amazon.com"),
            title="Samsung Galaxy S24 Ultra 5G AI Smartphone - 256GB, Titanium Gray, S Pen Included",
            brand="Samsung",
            category="Smartphones & Tablets",
            created_at=MOCK_NOW - timedelta(days=120),
        )
        self._catalog_cards[asin_10] = CatalogProduct(
            asin=asin_10,
            title="Samsung Galaxy S24 Ultra 5G AI Smartphone - 256GB, Titanium Gray, S Pen Included",
            brand="Samsung",
            category="Smartphones & Tablets",
            price=Decimal("1149.00"),
            list_price=Decimal("1299.00"),
            currency="USD",
            rating=Decimal("4.6"),
            review_count=5280,
            image_url="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="Save $150 • Prime Eligible",
            ai_verdict=DecisionVerdict.BUY,
            ai_verdict_summary="Verified 12% Discount ($1,149 vs $1,299 MSRP). Exceptional display outdoor readability.",
            specs=["Snapdragon 8 Gen 3", "200MP Quad Telephoto", "2600 nits Anti-Reflective AMOLED", "Integrated S-Pen"],
            marketplace="amazon.com",
            is_fixture=True,
        )
        self._price_histories[asin_10] = [
            PriceSnapshot(
                asin=asin_10,
                timestamp=MOCK_NOW - timedelta(days=d),
                currency="USD",
                amount=Decimal("1149.00") if d <= 10 else Decimal("1299.00"),
                list_price=Decimal("1299.00"),
                is_deal=(d <= 10),
                seller_type=SellerType.AMAZON_1P,
                in_stock=True,
            )
            for d in range(60, 0, -1)
        ]
        self._reviews[asin_10] = [
            ReviewRecord(
                review_id="REV-SAM-001",
                asin=asin_10,
                rating=Decimal("5.0"),
                title="Gorilla Armor anti-reflective screen is revolutionary",
                body="Reading in direct bright sunlight has zero reflections. The flat display makes the S Pen so much easier to use.",
                review_date=MOCK_NOW - timedelta(days=18),
                is_verified_purchase=True,
                helpful_votes=92,
                aspect_tags=["display", "performance"],
            )
        ]

        # -------------------------------------------------------------
        # FIXTURE 11: B0BADANC01 - SoundWave BassPod Pro Earbuds (High Defect Earbuds)
        # -------------------------------------------------------------
        asin_11 = "B0BADANC01"
        self._catalogs[asin_11] = ProductIdentity(
            asin=asin_11,
            marketplace="amazon.com",
            canonical_url=build_canonical_url(asin_11, "amazon.com"),
            title="SoundWave BassPod Pro Wireless Earbuds - Active Noise Canceling with 40H Playtime",
            brand="SoundWave",
            category="Audio & Headphones",
            created_at=MOCK_NOW - timedelta(days=90),
        )
        self._catalog_cards[asin_11] = CatalogProduct(
            asin=asin_11,
            title="SoundWave BassPod Pro Wireless Earbuds - Active Noise Canceling with 40H Playtime",
            brand="SoundWave",
            category="Audio & Headphones",
            price=Decimal("59.99"),
            list_price=Decimal("149.99"),
            currency="USD",
            rating=Decimal("4.2"),
            review_count=1820,
            image_url="https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="Deal of the Day • Claimed 60% Off",
            ai_verdict=DecisionVerdict.DONT_BUY,
            ai_verdict_summary="High Defect Alert: 42% of verified reviews cite right earbud audio dropouts and loud hiss within 30 days.",
            specs=["Hybrid ANC", "40hr Battery with Case", "Bluetooth 5.3", "IPX7 Waterproof"],
            marketplace="amazon.com",
            is_fixture=True,
        )
        self._price_histories[asin_11] = [
            PriceSnapshot(
                asin=asin_11,
                timestamp=MOCK_NOW - timedelta(days=d),
                currency="USD",
                amount=Decimal("59.99"),
                list_price=Decimal("149.99"),
                is_deal=True,
                seller_type=SellerType.FBA_3P,
                in_stock=True,
            )
            for d in range(45, 0, -1)
        ]
        self._reviews[asin_11] = [
            ReviewRecord(
                review_id="REV-SW-001",
                asin=asin_11,
                rating=Decimal("1.0"),
                title="Right earbud constantly disconnects and produces buzzing hiss",
                body="Worked for 2 weeks, then the right bud started dropping connection and producing an unbearable buzzing sound.",
                review_date=MOCK_NOW - timedelta(days=9),
                is_verified_purchase=True,
                helpful_votes=63,
                aspect_tags=["defect", "build_quality"],
            ),
            ReviewRecord(
                review_id="REV-SW-002",
                asin=asin_11,
                rating=Decimal("1.0"),
                title="Microphone is completely unusable on phone calls",
                body="People told me I sounded like I was underwater. Very poor microphone quality and connection cutting out.",
                review_date=MOCK_NOW - timedelta(days=14),
                is_verified_purchase=True,
                helpful_votes=27,
                aspect_tags=["defect", "performance"],
            ),
        ]

        # -------------------------------------------------------------
        # FIXTURE 12: B09VPHVT2Z - Anker 737 Power Bank (PowerCore 24K) 140W
        # -------------------------------------------------------------
        asin_12 = "B09VPHVT2Z"
        self._catalogs[asin_12] = ProductIdentity(
            asin=asin_12,
            marketplace="amazon.com",
            canonical_url=build_canonical_url(asin_12, "amazon.com"),
            title="Anker 737 Power Bank (PowerCore 24K), 24,000mAh 3-Port Portable Charger with 140W Output",
            brand="Anker",
            category="Tech Accessories",
            created_at=MOCK_NOW - timedelta(days=240),
        )
        self._catalog_cards[asin_12] = CatalogProduct(
            asin=asin_12,
            title="Anker 737 Power Bank (PowerCore 24K), 24,000mAh 3-Port Portable Charger with 140W Output",
            brand="Anker",
            category="Tech Accessories",
            price=Decimal("109.99"),
            list_price=Decimal("149.99"),
            currency="USD",
            rating=Decimal("4.7"),
            review_count=11400,
            image_url="https://images.unsplash.com/photo-1609592426038-f94ca2376991?auto=format&fit=crop&w=600&q=80",
            prime=True,
            deal_badge="Prime Exclusive • 27% Off",
            ai_verdict=DecisionVerdict.BUY,
            ai_verdict_summary="Verified Deal at All-Time Low ($109.99). Genuine 140W bidirectional charging verified.",
            specs=["24,000mAh Capacity", "140W USB-C Two-Way Fast Charge", "Smart Digital Display", "GaNPrime Tech"],
            marketplace="amazon.com",
            is_fixture=True,
        )
        self._price_histories[asin_12] = [
            PriceSnapshot(
                asin=asin_12,
                timestamp=MOCK_NOW - timedelta(days=d),
                currency="USD",
                amount=Decimal("109.99") if d <= 12 else Decimal("149.99"),
                list_price=Decimal("149.99"),
                is_deal=(d <= 12),
                seller_type=SellerType.AMAZON_1P,
                in_stock=True,
            )
            for d in range(60, 0, -1)
        ]
        self._reviews[asin_12] = [
            ReviewRecord(
                review_id="REV-ANK-001",
                asin=asin_12,
                rating=Decimal("5.0"),
                title="Charges my 16\" MacBook Pro at full speed",
                body="The digital screen showing wattage draw for each port is wonderful. Built like a brick and holds charge for weeks.",
                review_date=MOCK_NOW - timedelta(days=22),
                is_verified_purchase=True,
                helpful_votes=78,
                aspect_tags=["battery", "performance", "build_quality"],
            )
        ]

    # --- Catalog Search & Query Methods ---

    def search_catalog(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        verdict: Optional[str] = None,
    ) -> List[CatalogProduct]:
        """Search and filter the Amazon product catalog with deterministic matching."""
        results = list(self._catalog_cards.values())

        if category and category.lower() not in ("all", "all categories"):
            cat_norm = category.lower().strip()
            results = [p for p in results if cat_norm in p.category.lower()]

        if verdict and verdict.lower() != "all":
            v_norm = verdict.upper().strip()
            results = [p for p in results if p.ai_verdict.value == v_norm]

        if query and query.strip():
            terms = [t for t in re.split(r"\s+", query.lower().strip()) if t]
            scored_results = []
            for p in results:
                haystack = f"{p.asin} {p.title} {p.brand} {p.category} {' '.join(p.specs)}".lower()
                matches = sum(1 for term in terms if term in haystack)
                if matches > 0:
                    scored_results.append((matches, p))
            scored_results.sort(key=lambda x: x[0], reverse=True)
            results = [p for _, p in scored_results]

        return results

    def get_catalog_product(self, asin: str) -> Optional[CatalogProduct]:
        """Retrieve catalog card view for a given ASIN."""
        norm_asin = asin.strip().upper()
        return self._catalog_cards.get(norm_asin)

    def find_best_asin_for_query(self, query: str) -> Optional[str]:
        """Find the most relevant product ASIN for a natural language product query."""
        cleaned = query.strip()
        # Direct ASIN lookup
        if cleaned.upper() in self._catalogs:
            return cleaned.upper()

        # Catalog search
        matches = self.search_catalog(query=cleaned)
        if matches:
            return matches[0].asin
        return None

    # --- Protocol Implementations with Provenance Wrappers ---

    def get_product(self, asin: str, marketplace: str = "amazon.com") -> ProvenanceEnvelope[ProductIdentity]:
        """Fetch canonical product identity enveloped in Mock Fixture provenance."""
        try:
            canonical_asin, _ = parse_asin_and_marketplace(asin)
        except InvalidASINError:
            # Check if query matches a product title or brand in catalog
            found_asin = self.find_best_asin_for_query(asin)
            if found_asin:
                canonical_asin = found_asin
            else:
                raise InvalidASINError(f"Fixture not found for query or ASIN '{asin}'.")

        if canonical_asin not in self._catalogs:
            raise InvalidASINError(f"Fixture not found for ASIN '{canonical_asin}'. Available: {list(self._catalogs.keys())}")

        product = self._catalogs[canonical_asin]
        raw_repr = product.model_dump_json()

        return ProvenanceEnvelope[ProductIdentity](
            source_type=SourceType.MOCK_FIXTURE,
            source_url=f"mock://fixture/catalog/{canonical_asin}",
            retrieved_at=MOCK_NOW,
            raw_hash_sha256=_compute_sha256(raw_repr),
            confidence_score=1.0,
            is_verified_source=False,
            is_fixture=True,
            payload=product,
        )

    def get_price_history(
        self, asin: str, marketplace: str = "amazon.com", lookback_days: int = 90
    ) -> ProvenanceEnvelope[List[PriceSnapshot]]:
        """Fetch price snapshots enveloped in Mock Fixture provenance."""
        try:
            canonical_asin, _ = parse_asin_and_marketplace(asin)
        except InvalidASINError:
            found_asin = self.find_best_asin_for_query(asin)
            if found_asin:
                canonical_asin = found_asin
            else:
                raise InvalidASINError(f"Price history fixture not found for ASIN or query '{asin}'.")

        if canonical_asin not in self._price_histories:
            raise InvalidASINError(f"Price history fixture not found for ASIN '{canonical_asin}'.")

        all_snapshots = self._price_histories[canonical_asin]
        cutoff = MOCK_NOW - timedelta(days=lookback_days)
        filtered = [s for s in all_snapshots if s.timestamp >= cutoff]

        raw_repr = f"count={len(filtered)}:first={filtered[0].timestamp if filtered else 'none'}"

        return ProvenanceEnvelope[List[PriceSnapshot]](
            source_type=SourceType.MOCK_FIXTURE,
            source_url=f"mock://fixture/prices/{canonical_asin}?lookback={lookback_days}",
            retrieved_at=MOCK_NOW,
            raw_hash_sha256=_compute_sha256(raw_repr),
            confidence_score=1.0,
            is_verified_source=False,
            is_fixture=True,
            payload=filtered,
        )

    def get_reviews(
        self, asin: str, marketplace: str = "amazon.com", limit: int = 100
    ) -> ProvenanceEnvelope[List[ReviewRecord]]:
        """Fetch customer review records enveloped in Mock Fixture provenance."""
        try:
            canonical_asin, _ = parse_asin_and_marketplace(asin)
        except InvalidASINError:
            found_asin = self.find_best_asin_for_query(asin)
            if found_asin:
                canonical_asin = found_asin
            else:
                raise InvalidASINError(f"Review fixture not found for ASIN or query '{asin}'.")

        if canonical_asin not in self._reviews:
            raise InvalidASINError(f"Review fixture not found for ASIN '{canonical_asin}'.")

        records = self._reviews[canonical_asin][:limit]
        raw_repr = f"count={len(records)}:ids={','.join(r.review_id for r in records)}"

        return ProvenanceEnvelope[List[ReviewRecord]](
            source_type=SourceType.MOCK_FIXTURE,
            source_url=f"mock://fixture/reviews/{canonical_asin}?limit={limit}",
            retrieved_at=MOCK_NOW,
            raw_hash_sha256=_compute_sha256(raw_repr),
            confidence_score=1.0,
            is_verified_source=False,
            is_fixture=True,
            payload=records,
        )
