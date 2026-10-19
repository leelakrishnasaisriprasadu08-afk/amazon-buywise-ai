# BuyWise AI — Phase 3: Streaming Decision Orchestrator

This document provides a complete technical walkthrough of **Phase 3**, explaining the multi-stage decision pipeline, real-time Server-Sent Events (SSE) streaming architecture, API endpoints, and verification tests.

---

## 1. Executive Summary & Design Goals

Phase 3 implements the heart of the BuyWise AI system: the **Agent Decision Orchestrator**.

### Key Capabilities Delivered:
1. **Multi-Stage Coordination:** Connects canonical identity resolution, deterministic price economics, review aspect forensics, and competitor comparison into an end-to-end reasoning engine.
2. **Sub-second Multi-Factor Decision Gate:** Evaluates 5 explicit threshold gates to produce an unambiguous verdict:
   * **`BUY`**: Genuine deal (percentile $\le 35\%$, all-time low) + positive aspect sentiment ($\ge 65\%$) + low defect rate ($< 10\%$).
   * **`WAIT`**: Artificial pre-sale markup detected OR cyclical high percentile ($> 65\%$).
   * **`DONT_BUY`**: Strictly superior alternative exists (e.g., college student laptop) OR high defect recurrence rate ($\ge 20\%$).
   * **`INSUFFICIENT_EVIDENCE`**: Unvetted listing with sparse history ($< 5$ price points or $< 2$ reviews).
3. **Real-time Server-Sent Events (SSE) Streaming:** Emits live milestone events (`RESOLVE`, `PRICING`, `REVIEWS`, `COMPARE`, `DECIDE`, `COMPLETE`) to eliminate spinning loaders and provide an interactive reasoning timeline.
4. **Permanent Audit Trail:** Automatically logs every recommendation report into the SQLite repository.

---

## 2. Multi-Stage Pipeline Sequence

```
 ┌───────────────┐
 │ User / Client │
 └───────┬───────┘
         │ 1. GET /api/v1/analyze/stream?input_text=B0COLLEGE1
         ▼
 ┌──────────────────────────────────────────────────────────────┐
 │                  AgentDecisionOrchestrator                   │
 ├──────────────────────────────────────────────────────────────┤
 │  Milestone 1: RESOLVE                                        │
 │  • Extract 10-char ASIN & marketplace                        │
 │  • Load canonical product identity                           │
 ├──────────────────────────────────────────────────────────────┤
 │  Milestone 2: PRICING (Exact Decimal Math)                   │
 │  • Calculate rolling 30d/90d medians & percentiles           │
 │  • Detect artificial MSRP markup before sale                 │
 ├──────────────────────────────────────────────────────────────┤
 │  Milestone 3: REVIEWS (Hybrid BM25 + RRF)                    │
 │  • Score 7 quality aspects with verified buyer weighting     │
 │  • Bind verbatim citation excerpts with review IDs           │
 │  • Calculate recurring defect rate                           │
 ├──────────────────────────────────────────────────────────────┤
 │  Milestone 4: COMPARE (Competitor Engine)                    │
 │  • Head-to-head feature deltas & price savings               │
 │  • Evaluate is_strictly_better superiority gate              │
 ├──────────────────────────────────────────────────────────────┤
 │  Milestone 5: DECIDE (Multi-Factor Gate)                     │
 │  • BUY / WAIT / DONT_BUY / INSUFFICIENT_EVIDENCE             │
 │  • Synthesize key reasons, risks, and missing evidence       │
 ├──────────────────────────────────────────────────────────────┤
 │  Milestone 6: COMPLETE                                       │
 │  • Persist to SQLiteAuditStore                               │
 │  • Emit final RecommendationReport JSON payload              │
 └──────────────────────────────────────────────────────────────┘
```

---

## 3. Server-Sent Events (SSE) Wire Format

When connecting to `GET /api/v1/analyze/stream?input_text={asin}`, the server transmits milestone frames:

### Milestone 1: Product Resolution
```http
event: milestone
data: {"step": 1, "stage": "RESOLVE_SUCCESS", "message": "Canonical identity verified: VendorX SlimBook 14 (amazon.in)", "data": {"asin": "B0COLLEGE1", ...}}
```

### Milestone 2: Pricing Intelligence
```http
event: milestone
data: {"step": 2, "stage": "PRICING_SUCCESS", "message": "Price metrics computed: Current INR 52000.00 (Rank: 50.00%, 90d Median: 52000.00)", "data": {"current_price": "52000.00", ...}}
```

### Milestone 3: Review Aspect & Defect Forensics
```http
event: milestone
data: {"step": 3, "stage": "REVIEWS_SUCCESS", "message": "Analyzed 2 reviews (100% verified). Defect rate: 50.0%.", "data": {"aspects": {...}, "defect_rate": 0.5}}
```

### Milestone 4: Competitor Alternative Evaluation
```http
event: milestone
data: {"step": 4, "stage": "COMPARE_SUCCESS", "message": "Compared with BenchmarkPro 14... (Strictly superior: true)", "data": {"price_delta": "2010.00", "is_strictly_better": true}}
```

### Milestone 6: Final Complete Report
```http
event: complete
data: {"step": 6, "stage": "COMPLETE", "message": "Recommendation ready: Verdict is DONT_BUY (Confidence: 90%)", "report": {"asin": "B0COLLEGE1", "verdict": "DONT_BUY", "confidence": 0.90, "summary": "We recommend against buying this model because a strictly superior alternative (BenchmarkPro 14) is available at a lower effective cost (saving INR 2010.00) with superior specifications.", ...}}
```

---

## 4. API Reference

### 1. Synchronous Endpoint: `POST /api/v1/analyze`
**Request Body:**
```json
{
  "input_text": "https://www.amazon.in/dp/B0COLLEGE1",
  "alternative_asin": "B0COLLEGE2"
}
```

**Response (200 OK):** Returns full `RecommendationReport` JSON with `verdict`, `confidence`, `summary`, `price_metrics`, `aspect_analysis`, and `alternative`.

---

### 2. Real-time Streaming Endpoint: `GET /api/v1/analyze/stream`
**Query Parameters:**
* `input_text` (required): ASIN or full Amazon product URL.
* `alternative_asin` (optional): Competitor ASIN to evaluate against.

**Response Headers:**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

---

## 5. Verification & Test Suite

Run the full pytest suite:
```powershell
.\.venv\Scripts\pytest.exe --tb=short
```

### Summary of Results:
```
tests/test_api.py .................................. [ 10%] (9 passed)
tests/test_asin_parser.py .......................... [ 45%] (28 passed)
tests/test_aspect_analyzer.py ..                     [ 47%] (2 passed)
tests/test_competitor_matcher.py .                   [ 48%] (1 passed)
tests/test_domain_models.py .......                  [ 57%] (7 passed)
tests/test_hybrid_retrieval.py ....                  [ 62%] (4 passed)
tests/test_mock_provider.py ........                 [ 71%] (8 passed)
tests/test_orchestrator.py ......                    [ 79%] (6 passed)
tests/test_pricing_engine.py .............           [ 95%] (13 passed)
tests/test_sqlite_store.py ....                      [100%] (4 passed)

============================= 82 passed, 1 warning in 2.60s =============================
```

### Key Behavioral Test Scenarios Verified:
* **Scenario 1 (`B08N5WRWNW` - MacBook M1):** Correctly yields `BUY` with 92% confidence (price at all-time low, positive verified sentiment).
* **Scenario 2 (`B09V3K3EXP` - Smartphone):** Correctly yields `WAIT` with 85% confidence (pre-sale MSRP markup detected).
* **Scenario 3 (`B07DEFECT0` - Mouse):** Correctly yields `DONT_BUY` with 88% confidence (recurring scroll wheel defect rate $\ge 20\%$).
* **Scenario 4 (`B0COLLEGE1` - College Laptop):** Correctly yields `DONT_BUY` (strictly superior `B0COLLEGE2` alternative available saving ₹2,010 with 16GB RAM and IPS display).
* **Scenario 5 (`B0NEWITEM0` - Generic Hub):** Correctly yields `INSUFFICIENT_EVIDENCE` with explicit missing evidence disclosures.
* **Streaming Milestones:** Verified that `stream_pipeline` yields formatted SSE chunks with milestones and complete events.
