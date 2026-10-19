# BuyWise AI — Phase 4 Walkthrough: Production-Grade Forensic UI & Streaming Decision Dashboard

## 1. Executive Summary

Phase 4 bridges the deterministic backend intelligence pipeline (Phases 1–3) with an enterprise-grade, realistic, and security-hardened React + TypeScript interface. Built specifically for the **Amazon Hackathon**, BuyWise AI is designed to combat buyer remorse, reduce e-commerce product return rates, and detect artificial discounts before checkout.

In accordance with strict production standards:
- **Zero Vibe-Coding**: Every component, interface, and line of code has an explicit functional role.
- **Zero Client Mock Data**: The frontend contains zero hardcoded catalogs or fabricated reports. All evaluations are powered dynamically by the live backend via Server-Sent Events (`/api/v1/analyze/stream`).
- **Deterministic Math Invariants**: Financial arithmetic (rolling medians, percentiles, savings deltas) is computed strictly in Python `Decimal` arithmetic and displayed without client-side modification.
- **Cryptographic Provenance**: Every verdict exposes raw SHA-256 payload digests, timestamped provenance envelopes, and verbatim verified review quotes.
- **Security & Privacy First**: An explicit Privacy, Security & Impartiality policy is integrated into the UI.

---

## 2. Architecture & File Structure

The Phase 4 frontend lives in the `frontend/` directory, built with **React 19**, **TypeScript**, and **Vite**:

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.tsx                 # Brand identity, security badge, Privacy modal trigger
│   │   ├── PrivacyModal.tsx           # Full Privacy, Security & Impartiality Policy modal
│   │   ├── VerdictBanner.tsx          # Decision badges (BUY, WAIT, DONT_BUY, INSUFFICIENT_EVIDENCE)
│   │   ├── PriceIntelligenceCard.tsx  # Price spectrum bar, percentile meter, markup flags
│   │   ├── AspectScorecards.tsx       # 7 aspect categories, defect counters, verbatim quotes
│   │   ├── CompetitorCard.tsx         # Alternative comparison, price delta, spec matrix
│   │   ├── ReasoningTimeline.tsx      # Real-time SSE stage tracker & streaming event log
│   │   └── AuditLedger.tsx            # Cryptographic SHA-256 provenance & missing evidence ledger
│   ├── services/
│   │   └── api.ts                     # SSE EventSource stream consumer & sync REST client
│   ├── types/
│   │   └── buywise.ts                 # TypeScript interfaces mirrored 1:1 from Pydantic backend
│   ├── App.tsx                        # Master application shell, landing page, state orchestration
│   ├── index.css                      # Enterprise dark mode design system (Vanilla CSS tokens)
│   └── main.tsx                       # React application root
├── vite.config.ts                     # Dev server proxy (/api -> http://127.0.0.1:8000)
└── package.json                       # Dependencies: react, react-dom, lucide-react
```

---

## 3. Forensic UI Design System

### 3.1 Color Palette & Visual Hierarchy
Designed with an enterprise dark mode palette inspired by high-trust security dashboards:
- **Base Background**: `#090d16` (Deep Obsidian)
- **Secondary Surfaces**: `#0f172a` (Slate Navy) with subtle 8% borders (`rgba(255, 255, 255, 0.08)`)
- **Accent Blue**: `#38bdf8` (Cyan Blue)
- **Amazon Gold**: `#ff9900`
- **Verdict Emerald**: `#10b981` (BUY)
- **Verdict Amber**: `#f59e0b` (WAIT)
- **Verdict Crimson**: `#f43f5e` (DON'T BUY)
- **Verdict Slate**: `#64748b` (INSUFFICIENT EVIDENCE)

### 3.2 High-Trust Landing Page
When a user visits the platform:
1. **Hero Title & Value Proposition**: Clearly communicates the platform's purpose: *"Don't guess. Audit the evidence before you buy."*
2. **Search & Canonical Resolution Bar**: Accepts both full Amazon product URLs and 10-character ASINs.
3. **Optional Competitor Input Field**: Expandable input to compare a target product directly against a specific competitor ASIN (e.g., `B0COMPET01`).
4. **Hackathon Demo Benchmarks**: 5 one-click benchmark chips designed to showcase the four distinct decision paths:
   - `B0COLLEGE1`: College Student Laptop (Triggers switch to upgradeable alternative, saving ₹2,010).
   - `B08N5WRWNW`: MacBook Air M1 (Genuine deal at all-time low $\rightarrow$ `BUY`).
   - `B09V3K3EXP`: Flagship Smartphone (Pre-sale MSRP markup $\rightarrow$ `WAIT`).
   - `B07DEFECT0`: Ergonomic Gaming Mouse (High 4.4★ but severe switch failure rate $\rightarrow$ `DONT_BUY`).
   - `B0NEWITEM0`: Compact 7-Port Hub (Brand new listing with only 1 review $\rightarrow$ `INSUFFICIENT_EVIDENCE`).
5. **4-Pillar Architectural Showcase**:
   - *Deterministic Price Math*: Rolling 30/90-day medians and percentile tracking.
   - *Review Aspect Forensics*: BM25 + Semantic scoring isolating verified reviews across 7 aspects.
   - *Objective Alternative Engine*: Spec and cost comparison with zero affiliate distortion.
   - *Cryptographic Provenance*: SHA-256 hashes and timestamped evidence envelopes.
6. **Security & Impartiality Guarantee Card**: Outlines explicit protections against credential harvesting, LLM arithmetic hallucinations, and ungrounded review-fraud accusations.

---

## 4. Component Deep Dive

### 4.1 Real-Time Streaming Reasoning Timeline (`ReasoningTimeline.tsx`)
Connects to `/api/v1/analyze/stream` using the browser's native `EventSource`. As each stage completes, a milestone is emitted and animated in real time:
1. **Step 1: Canonical Resolution** (`RESOLVE`) — Validates URL/ASIN and fetches catalog metadata.
2. **Step 2: Deterministic Pricing** (`PRICING`) — Computes percentiles, median comparisons, and markup alerts.
3. **Step 3: Review Aspect Forensics** (`REVIEWS`) — Runs BM25 and semantic scoring, grouping quotes by aspect.
4. **Step 4: Competitor Deltas** (`COMPARE`) — Evaluates alternatives and computes potential savings.
5. **Step 5: Multi-Factor Gate** (`DECIDE`) — Synthesizes confidence scores and emits the final report.

### 4.2 Verdict Banner (`VerdictBanner.tsx`)
Presents the executive summary and decision metrics:
- Large badge with contextual icon and color.
- Confidence score meter with evidence volume indicators (reviews analyzed, price snapshots checked).
- Highlighted key reason box (e.g., *"Hardware Defect Alert: 18.2% of verified reviews report scroll wheel failure within 3 months"*).
- Direct link to the canonical Amazon listing.

### 4.3 Price Intelligence Card (`PriceIntelligenceCard.tsx`)
- Current price vs list price (MSRP) and effective discount percentage.
- **Price Range Track**: Visual gauge displaying current price position relative to 30-day minimum, 90-day median, and 30-day maximum.
- **Percentile Indicator**: Displays historical price position ($0\% = \text{lowest ever}$, $100\% = \text{highest ever}$).
- **Artificial Markup Warning**: Highlighted callout if the seller inflated the strike-through price right before putting the item on sale.

### 4.4 Aspect Scorecards (`AspectScorecards.tsx`)
- Tabs for 7 hardware categories: *Performance*, *Battery*, *Build Quality*, *Display*, *Software/OS*, *Price/Value*, *Durability*.
- Overall satisfaction progress bar and verified review count.
- **Recurring Defect Warning**: Flags specific defect rates when they exceed 10% of verified reviews.
- **Verbatim Citations**: Quotes from verified Amazon purchasers, including review rating, date, and verified purchase badge.

### 4.5 Competitor Alternative Card (`CompetitorCard.tsx`)
When a superior alternative is discovered:
- Side-by-side comparison between the target product and the alternative.
- Verified cost delta (e.g., *"Save ₹2,010 (3.9%)"* or *"Superior Specs for Same Price"*).
- Feature-by-feature matrix highlighting advantages (e.g., *Upgradeable DDR5 RAM* vs *Soldered 8GB RAM*).
- One-click button to immediately pivot and run a full audit on the alternative.

### 4.6 Cryptographic Audit Ledger (`AuditLedger.tsx`)
An expandable transparency panel that proves every claim:
- Report ID and generation timestamp.
- Cryptographic SHA-256 payload digest for data tampering prevention.
- Data envelope provenance: Source URL, retrieval timestamp, and provider fixture disclosure.
- Missing evidence checklist: Discloses whether price history or review volume had limitations.

### 4.7 Privacy & Policy Modal (`PrivacyModal.tsx`)
Accessible from the header navigation, landing page security box, and footer:
1. **Zero Credential Access**: Never requests, accesses, or stores user logins, cookies, or payment info.
2. **Separation of Math from LLM**: 100% pure Python `Decimal` computations with 0-tolerance invariants.
3. **Cryptographic Provenance**: Every claim backed by raw SHA-256 envelopes and citation URLs.
4. **100% Impartiality Guarantee**: Zero affiliate links, zero paid promotions, and zero brand favoritism.

---

## 5. Verification & Build Integrity

### 5.1 TypeScript Compilation & Vite Build
```bash
cd frontend
npm run build
```
**Output:**
```
> frontend@0.0.0 build
> tsc -b && vite build

vite v8.3.4 building client environment for production...
transforming...
✓ 1918 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-BRzVkv6c.css   24.78 kB │ gzip:  4.99 kB
dist/assets/index-DlBqoznm.js   265.64 kB │ gzip: 81.74 kB
✓ built in 1.36s
```
*Zero compilation errors. Zero bundle warnings.*

### 5.2 Backend Test Suite
```bash
.venv\Scripts\pytest
```
**Output:**
```
82 passed, 1 warning in 3.19s (100% test pass rate)
```

---

## 6. How to Run the End-to-End System

### Terminal 1: Backend API (FastAPI)
```powershell
# From project root
.venv\Scripts\activate
uvicorn src.buywise.api.app:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: `http://127.0.0.1:8000/docs`

### Terminal 2: Frontend UI (Vite + React)
```powershell
# In a second terminal
cd frontend
npm run dev
```
Dashboard will be live at: `http://localhost:5173`

Enter any Amazon product URL or ASIN (or click one of the hackathon demo chips) to watch the streaming evidence audit in real time!
