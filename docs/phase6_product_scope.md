# Phase 6 Product Scope — AI CV Fit

> **Created:** 2026-06-17
> **Baseline commit:** `04ab4fa` (main)
> **Purpose:** Park high-risk JobReady-like features out of the demo path with a clear, minimal
> Phase 6 definition. Nothing here is required for the Phase 5 demo. Do not build payment now.

---

## 1. Lightweight substitutes for high-risk benchmark features

| Benchmark feature | Too risky because | Lightweight substitute (demo-safe) | Phase |
|---|---|---|---|
| Full job marketplace/search | Needs scraping/ingestion, search infra, data licensing | **Target Jobs / Saved JD Workspace** — reuse application+JD creation | 6 |
| Pricing / credits / payment | Real money, PCI, PayOS/Stripe integration, refunds | **Static plan visibility / usage-policy note** — no checkout | 6 |
| Chatbot / LLM assistant | Latency, cost, hallucination/guardrail risk | **Static Help Assistant / Guided FAQ drawer** (`/help`) | 5 (shell) / 6 (LLM) |
| Learning academy / course marketplace | Content sourcing, catalog, payments | **`/learning` roadmap** from analysis/readiness gaps (reuse `LearningRoadmap`) | 5 (shell) |
| Interview room with video/camera | WebRTC, media permissions, recording/privacy | **Structured interview practice** — question list + answer box + rubric/history (exists) | 5 (done) |
| Recruiter portal | Separate role model, ATS-like features, permissions | Position product as candidate-first; defer recruiter role | 6 |

**Principle:** substitutes reuse existing flows/components and add **no backend migration, no payment, no fake data**.

---

## 2. Phase 6 candidate features

For each: why not now / minimum viable version / dependencies / suggested milestone.

### 2.1 Full job marketplace & search
- **Why not now:** Requires job ingestion, search/index, and ongoing data ops; high product + legal risk.
- **MVP:** "Target Jobs" view built on existing applications; optional manual JD import; no external scraping.
- **Dependencies:** Possibly a "list analyses/applications" endpoint; search later.
- **Milestone:** Phase 6.1.

### 2.2 Payment / credits / checkout (PayOS/Stripe)
- **Why not now:** Real money handling, compliance, fraud, refunds; out of demo scope.
- **MVP:** Static plan page describing tiers + usage limits; no transactions.
- **Dependencies:** Billing provider, wallet/ledger schema (migration), webhooks.
- **Milestone:** Phase 6.3.

### 2.3 Real chatbot / LLM assistant
- **Why not now:** Latency/cost, guardrail and privacy exposure for user data.
- **MVP:** Static guided FAQ (`/help`) covering the workflow; upgrade to retrieval/LLM later behind backend support.
- **Dependencies:** Assistant backend endpoint, guardrails, rate limiting.
- **Milestone:** Phase 6.2.

### 2.4 Full learning/course marketplace
- **Why not now:** Catalog, content licensing, payments.
- **MVP:** `/learning` roadmap from analysis gaps (Phase 5 shell); curated external links later.
- **Dependencies:** Content model; optional partner integrations.
- **Milestone:** Phase 6.2.

### 2.5 Advanced interview room (video/camera)
- **Why not now:** WebRTC complexity, media/privacy, recording storage.
- **MVP:** Keep text-based structured practice; optionally add timer/voice later.
- **Dependencies:** Media infra, consent/privacy review.
- **Milestone:** Phase 6.4.

### 2.6 Recruiter portal
- **Why not now:** New role/permission model and ATS-like surface; doubles product scope.
- **MVP:** Read-only "shareable readiness summary" before a full portal.
- **Dependencies:** Roles/permissions, sharing model.
- **Milestone:** Phase 6.4.

### 2.7 Admin analytics dashboard
- **Why not now:** GA4 already covers product analytics for the demo.
- **MVP:** Use GA4 Explorations; build in-app admin later if needed.
- **Dependencies:** Admin auth, aggregation queries.
- **Milestone:** Phase 6.3.

### 2.8 Other parked items
Resume-template marketplace, notification system, recommendation engine beyond existing analysis — all **Phase 6**, each gated on a clear backend contract and low implementation risk before adoption.

---

## 3. Phase 5 vs Phase 6 boundary (summary)

**Keep before demo (FE-only / docs-only, no migration, no payment, no fake claims):**
journey polish (CTAs, attach UX, empty states), `/learning` shell, `/help` static shell, demo seed + E2E sign-off docs, analytics verification.

**Move to Phase 6:**
job marketplace/search, payment/credits, real chatbot, course marketplace, video interview room, recruiter portal, admin analytics dashboard, resume-template marketplace, notifications, recommendation engine.
