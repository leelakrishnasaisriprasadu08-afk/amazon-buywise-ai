"""Thread-safe SQLite storage for caching product records, price snapshots, and audit trails."""

from datetime import datetime, timezone
from decimal import Decimal
import json
import sqlite3
import threading
from typing import List, Optional

from buywise.models.identity import ProductIdentity
from buywise.models.price import PriceSnapshot, SellerType
from buywise.models.provenance import ProvenanceEnvelope
from buywise.models.report import RecommendationReport


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
    asin TEXT PRIMARY KEY,
    marketplace TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    title TEXT,
    brand TEXT,
    category TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS price_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asin TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    currency TEXT NOT NULL,
    amount TEXT NOT NULL,
    list_price TEXT,
    is_deal INTEGER NOT NULL,
    deal_type TEXT,
    seller_type TEXT NOT NULL,
    in_stock INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_price_snapshots_asin_ts ON price_snapshots(asin, timestamp);

CREATE TABLE IF NOT EXISTS evidence_audit (
    evidence_id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_url TEXT NOT NULL,
    retrieved_at TEXT NOT NULL,
    raw_hash_sha256 TEXT,
    confidence_score REAL NOT NULL,
    is_verified_source INTEGER NOT NULL,
    is_fixture INTEGER NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recommendation_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asin TEXT NOT NULL,
    verdict TEXT NOT NULL,
    confidence REAL NOT NULL,
    summary TEXT NOT NULL,
    report_json TEXT NOT NULL,
    generated_at TEXT NOT NULL
);
"""


class SQLiteAuditStore:
    """Thread-safe SQLite repository with Decimal preservation via TEXT columns."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        self._shared_conn: Optional[sqlite3.Connection] = None

        if self.db_path == ":memory:":
            # Retain single persistent in-memory connection
            self._shared_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._shared_conn.row_factory = sqlite3.Row
            self._shared_conn.execute("PRAGMA foreign_keys = ON;")

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._shared_conn is not None:
            return self._shared_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        conn = self._get_connection()
        with self._lock:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    def save_product(self, product: ProductIdentity) -> None:
        """Upsert a canonical product record."""
        sql = """
        INSERT INTO products (asin, marketplace, canonical_url, title, brand, category, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(asin) DO UPDATE SET
            title = excluded.title,
            brand = excluded.brand,
            category = excluded.category;
        """
        conn = self._get_connection()
        with self._lock:
            conn.execute(
                sql,
                (
                    product.asin,
                    product.marketplace,
                    product.canonical_url,
                    product.title,
                    product.brand,
                    product.category,
                    product.created_at.isoformat(),
                ),
            )
            conn.commit()

    def get_product(self, asin: str) -> Optional[ProductIdentity]:
        """Retrieve a product by ASIN."""
        conn = self._get_connection()
        with self._lock:
            row = conn.execute("SELECT * FROM products WHERE asin = ?", (asin.upper(),)).fetchone()
            if not row:
                return None
            return ProductIdentity(
                asin=row["asin"],
                marketplace=row["marketplace"],
                canonical_url=row["canonical_url"],
                title=row["title"],
                brand=row["brand"],
                category=row["category"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def save_price_snapshots(self, snapshots: List[PriceSnapshot]) -> None:
        """Bulk insert price snapshots preserving exact Decimal precision as strings."""
        if not snapshots:
            return
        sql = """
        INSERT INTO price_snapshots (
            asin, timestamp, currency, amount, list_price, is_deal, deal_type, seller_type, in_stock
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = self._get_connection()
        with self._lock:
            params = [
                (
                    s.asin,
                    s.timestamp.isoformat(),
                    s.currency,
                    str(s.amount),
                    str(s.list_price) if s.list_price is not None else None,
                    1 if s.is_deal else 0,
                    s.deal_type,
                    s.seller_type.value,
                    1 if s.in_stock else 0,
                )
                for s in snapshots
            ]
            conn.executemany(sql, params)
            conn.commit()

    def get_price_history(self, asin: str) -> List[PriceSnapshot]:
        """Fetch all historical price snapshots for an ASIN ordered chronologically."""
        sql = "SELECT * FROM price_snapshots WHERE asin = ? ORDER BY timestamp ASC"
        conn = self._get_connection()
        with self._lock:
            rows = conn.execute(sql, (asin.upper(),)).fetchall()
            return [
                PriceSnapshot(
                    asin=r["asin"],
                    timestamp=datetime.fromisoformat(r["timestamp"]),
                    currency=r["currency"],
                    amount=Decimal(r["amount"]),
                    list_price=Decimal(r["list_price"]) if r["list_price"] else None,
                    is_deal=bool(r["is_deal"]),
                    deal_type=r["deal_type"],
                    seller_type=SellerType(r["seller_type"]),
                    in_stock=bool(r["in_stock"]),
                )
                for r in rows
            ]

    def save_evidence_envelope(self, envelope: ProvenanceEnvelope) -> None:
        """Record evidence provenance for permanent auditability."""
        sql = """
        INSERT OR REPLACE INTO evidence_audit (
            evidence_id, source_type, source_url, retrieved_at, raw_hash_sha256,
            confidence_score, is_verified_source, is_fixture, payload_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = self._get_connection()
        with self._lock:
            payload_str = json.dumps(
                envelope.payload.model_dump(mode="json")
                if hasattr(envelope.payload, "model_dump")
                else envelope.payload
            )
            conn.execute(
                sql,
                (
                    envelope.evidence_id,
                    envelope.source_type.value,
                    envelope.source_url,
                    envelope.retrieved_at.isoformat(),
                    envelope.raw_hash_sha256,
                    envelope.confidence_score,
                    1 if envelope.is_verified_source else 0,
                    1 if envelope.is_fixture else 0,
                    payload_str,
                ),
            )
            conn.commit()

    def save_recommendation_report(self, report: RecommendationReport) -> int:
        """Audit log a generated recommendation report and return the audit ID."""
        sql = """
        INSERT INTO recommendation_audit (
            asin, verdict, confidence, summary, report_json, generated_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        conn = self._get_connection()
        with self._lock:
            cur = conn.execute(
                sql,
                (
                    report.asin,
                    report.verdict.value,
                    report.confidence,
                    report.summary,
                    report.model_dump_json(),
                    report.generated_at.isoformat(),
                ),
            )
            conn.commit()
            return cur.lastrowid or 0
