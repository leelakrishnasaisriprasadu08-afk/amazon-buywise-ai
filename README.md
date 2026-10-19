# BuyWise AI — Shopping Intelligence System

A modular, evidence-grounded shopping intelligence system for Amazon products that separates deterministic computations from probabilistic LLM reasoning.

---

## Phase 1: Foundation Features

* **Typed Domain Contracts (Pydantic v2):**
  * `ProductIdentity`: Normalized 10-character ASIN validation, marketplace normalization, canonical URL construction.
  * `ProvenanceEnvelope[T]`: Cryptographic and verifiable provenance tracking (`evidence_id`, `source_type`, `source_url`, `retrieved_at`, `raw_hash_sha256`, `confidence_score`, `is_fixture`).
  * `ReviewRecord`: Normalized reviews with Decimal ratings ($1.0 - 5.0$), verified purchase badge tracking, and helpful votes.
  * `PriceSnapshot`: Immutable point-in-time pricing observations with strictly currency-safe `Decimal` arithmetic.
  * `PriceMetrics`: Deterministic calculations (min, max, median, percentile rank, rolling 30d/90d medians, true discount percentage, artificial discount detection).
  * `RecommendationReport`: Evidence-grounded verdict (`BUY`, `WAIT`, `DONT_BUY`, `INSUFFICIENT_EVIDENCE`) with explicit `missing_evidence` tracking.
* **Deterministic ASIN & URL Parser:**
  * Extracts ASINs from standard `/dp/`, `/gp/product/`, mobile `/gp/aw/d/`, regional domains (`.com`, `.in`, `.co.uk`, `.de`, `.co.jp`), and query parameters.
  * Rejects non-Amazon URLs, invalid character sets, malformed lengths, and empty strings.
* **Strict Currency-Safe Math Engine:**
  * Uses Python `Decimal` with `ROUND_HALF_UP` precision.
  * Explicitly forbids cross-currency arithmetic (`CurrencyMismatchError`).
  * Detects pre-sale artificial MSRP markups.
* **Provider Protocols & MockFixtureProvider:**
  * Defined `@runtime_checkable` protocols: `ProductCatalogProvider`, `PriceHistoryProvider`, `ReviewProvider`.
  * `MockFixtureProvider` explicitly flags all fixtures with `source_type="mock_fixture"` and `is_fixture=True`. Never masquerades as live data.
* **Thread-Safe SQLite Audit Repository:**
  * Persists product catalogs, price snapshots (with exact Decimal strings), and audit trails.
* **FastAPI Entry Points:**
  * `GET /health`
  * `POST /api/v1/parse-product`
  * `GET /api/v1/products/{asin}/price-metrics`

---

## Phase 2: Hybrid Retrieval & Review Aspect Forensics

* **Hybrid Retrieval (BM25Okapi + Semantic Scoring + RRF):**
  * Sub-millisecond filtering of customer review corpora using `rank-bm25`.
  * Reciprocal Rank Fusion ($k=60$) with verified purchaser trust multipliers.
* **Aspect Sentiment & Grounded Citations:**
  * Evaluates 7 core dimensions (`battery`, `build_quality`, `display`, `performance`, `value`, `usability`, `defect`).
  * Binds verbatim review quotes and timestamps directly to aspect ratings.
* **Defect Forensics Engine:**
  * Clusters recurring failure patterns (e.g. soldered RAM bottlenecks, TN screen washed contrast, hinge breakdown).
* **Competitor Comparison Engine:**
  * Computes head-to-head feature deltas, price deltas, and `is_strictly_better` superiority invariants.
* **College Laptop Hackathon Benchmark:**
  * Full scenario verified: Target `B0COLLEGE1` (VendorX ₹52,000) vs Alternative `B0COLLEGE2` (BenchmarkPro ₹49,990 saving ₹2,010 with 16GB RAM and IPS display).
* **Phase 2 REST Endpoints:**
  * `GET /api/v1/products/{asin}/aspects`
  * `GET /api/v1/products/{asin}/alternatives`

Detailed walkthrough and math available in [docs/PHASE_2_WALKTHROUGH.md](file:///C:/Users/leela/OneDrive/Desktop/buywise%20ai/amazon-buywise-ai/docs/PHASE_2_WALKTHROUGH.md).

---

## Phase 3: Streaming Decision Orchestrator

* **Agent Decision Orchestrator (`AgentDecisionOrchestrator`):**
  * Coordinates the complete 6-stage shopping intelligence pipeline: `RESOLVE` ➔ `PRICING` ➔ `REVIEWS` ➔ `COMPARE` ➔ `DECIDE` ➔ `COMPLETE`.
  * Deterministic multi-factor gate evaluating `BUY`, `WAIT`, `DONT_BUY`, and `INSUFFICIENT_EVIDENCE`.
* **Real-time Server-Sent Events (SSE) Streaming:**
  * Real-time reasoning telemetry streamed over HTTP (`text/event-stream`).
  * Emits milestone events so frontend UIs update progressively in sub-seconds.
* **Synchronous & Streaming Endpoints:**
  * `POST /api/v1/analyze`: Synchronous full report generation.
  * `GET /api/v1/analyze/stream`: Live SSE milestone streaming.

Detailed architecture and event formats available in [docs/PHASE_3_WALKTHROUGH.md](file:///C:/Users/leela/OneDrive/Desktop/buywise%20ai/amazon-buywise-ai/docs/PHASE_3_WALKTHROUGH.md).

---

## Phase 4: Production-Grade Forensic UI & Streaming Decision Dashboard

* **Enterprise-Grade Forensic Interface (React 19 + TypeScript + Vite):**
  * Modern, high-trust dark mode interface built strictly with Vanilla CSS tokens and enterprise aesthetics.
  * Zero "vibe-coding" and zero client mock data: every component consumes live Server-Sent Events from the backend.
* **4-Pillar Architecture Showcase:**
  * Displays the core forensic mechanisms directly on the landing page:
    1. *Deterministic Price Math* (rolling 30/90-day medians, percentile gauge, artificial markup alert).
    2. *Review Aspect Forensics* (BM25 + Semantic scoring across 7 hardware aspects with verbatim citations).
    3. *Objective Alternative Engine* (spec-by-spec comparison and verified savings calculation).
    4. *Cryptographic Evidence Provenance* (raw SHA-256 digests and timestamped audit envelopes).
* **Security & Privacy Posture:**
  * Integrated **Privacy, Security & Impartiality Policy Modal** (`PrivacyModal.tsx`).
  * Explicit guarantees: Zero credential storage, zero LLM arithmetic, zero ungrounded fraud accusations, and zero affiliate distortion.
* **Real-Time Streaming Reasoning Timeline:**
  * Displays live SSE milestones (`RESOLVE` ➔ `PRICING` ➔ `REVIEWS` ➔ `COMPARE` ➔ `DECIDE`) as the engine evaluates listings in real time.
* **Interactive Hackathon Benchmark Suite:**
  * One-click audit chips for live judge demonstration:
    * `B0COLLEGE1`: College Student Laptop (VendorX ₹52K $\rightarrow$ Switch & Save ₹2,010).
    * `B08N5WRWNW`: Apple MacBook Air M1 ($749 $\rightarrow$ Genuine deal at all-time low $\rightarrow$ `BUY`).
    * `B09V3K3EXP`: Flagship Smartphone ($899 $\rightarrow$ Pre-sale MSRP markup $\rightarrow$ `WAIT`).
    * `B07DEFECT0`: Ergonomic Gaming Mouse (4.4★ but severe switch failure $\rightarrow$ `DONT_BUY`).
    * `B0NEWITEM0`: Compact 7-Port Hub (1 review $\rightarrow$ `INSUFFICIENT_EVIDENCE`).

Detailed architecture and component design available in [docs/PHASE_4_WALKTHROUGH.md](file:///C:/Users/leela/OneDrive/Desktop/buywise%20ai/amazon-buywise-ai/docs/PHASE_4_WALKTHROUGH.md).

---

## Setup & Running the Complete System

### 1. Requirements
* Python 3.12+ (Windows compatible)
* Node.js 18+ and npm

### 2. 1-Click Launch (Recommended for Demos & Presentations)
```powershell
# Double-click start.bat in Windows Explorer OR execute via PowerShell:
.\start.ps1
```
This automatically initializes the environment, starts the FastAPI backend (port 8000), starts the Vite React frontend (port 5173), and opens your default browser!

### 3. Manual Launch & Full Test Suite (90 Passing Tests)
```powershell
# 1. Create & activate virtual environment
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -e .
pip install -r requirements.txt

# 3. Run full backend test suite (90 passing tests)
.\.venv\Scripts\pytest.exe -v

# 4. Launch FastAPI server (Terminal 1)
.\.venv\Scripts\uvicorn.exe buywise.api.app:app --reload --port 8000

# 5. Launch Vite frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

Interactive API documentation is available at `http://localhost:8000/docs`, and the live dashboard is at `http://localhost:5173`.


