# Phase 5 Demo Readiness Plan — AI CV Fit

> **Created:** 2026-06-17
> **Baseline commit:** `04ab4fa` (main)
> **Scope:** Planning. Frontend-only / docs-only changes recommended. No backend, no migrations,
> no payment, no fake data/claims. Phase 5 is **not** marked complete by this doc.
> Complements existing `docs/phase5_demo_checklist.md` (does not replace it).

---

## 1. Must-fix before presentation (ruthless: 5 items)

### MF1 — Pre-seed demo data and document it
- **Why:** AI generation latency is the #1 live-demo risk; a pre-attached analysis removes it.
- **Area:** demo account; `docs/phase5_demo_checklist.md` (extend), this plan.
- **User-visible improvement:** Every demo page has real content instantly.
- **Backend dep:** None (uses existing flows to create data).
- **PR boundary:** PR D (docs + seed instructions).
- **Risk:** LOW.
- **Acceptance:** Demo account has ≥1 completed analysis attached to ≥1 application, ≥1 evidence item, generated cover letter + package, ≥1 interview answer.

### MF2 — Fix the "attach analysis" friction (manual Job ID paste)
- **Why:** Most confusing transition; a presenter pasting a UUID looks broken.
- **Area:** `frontend/src/app/applications/[id]/page.js` (attach form).
- **User-visible improvement:** Choose a recent analysis from a list instead of pasting an ID; or, for demo, arrive pre-attached.
- **Backend dep:** FE-only picker possible from history data; a "list my analyses" endpoint would be cleaner (Phase 6).
- **PR boundary:** PR A (journey polish) — FE-only; pre-seed covers the demo regardless.
- **Risk:** LOW_FRONTEND_ONLY.
- **Acceptance:** From application detail, user can attach without typing a raw ID, OR demo data is pre-attached and the path is documented.

### MF3 — Clear "next step" CTAs across the core flow
- **Why:** Story coherence — judges should never wonder "what now?".
- **Area:** result dashboard (`ResultCardV2`), `/applications/[id]`, package/cover-letter pages.
- **User-visible improvement:** Each stage points to the next (Result → Create application → Interview → Cover letter → Package).
- **Backend dep:** None.
- **PR boundary:** PR A.
- **Risk:** LOW_FRONTEND_ONLY.
- **Acceptance:** Every core page reaches the next stage in 1–2 clicks.

### MF4 — `/learning` shell from existing analysis data
- **Why:** Benchmark has an academy; we already have `LearningRoadmap` content with no home.
- **Area:** new `frontend/src/app/learning/page.js` reusing `components/results/LearningRoadmap.jsx`.
- **User-visible improvement:** A coherent upskilling page linked from result/readiness.
- **Backend dep:** None (reuses analysis-derived items; static fallback if none).
- **PR boundary:** PR B.
- **Risk:** LOW_FRONTEND_ONLY.
- **Acceptance:** `/learning` renders roadmap items (or a clear empty/seed state) and is linked from nav or readiness.

### MF5 — Consistent empty/loading/error states on demo path
- **Why:** Empty interview/cover-letter/package pages without analysis can look broken.
- **Area:** interview/cover-letter/package pages + `EmptyStatePage`.
- **User-visible improvement:** Friendly guidance instead of blank panels.
- **Backend dep:** None.
- **PR boundary:** PR A.
- **Risk:** LOW_FRONTEND_ONLY.
- **Acceptance:** Each demo route shows a purposeful empty/loading/error state.

---

## 2. Suggested PR sequence

| PR | Name | Scope | Files likely touched | User-visible outcome | Risk | Depends on | Test plan |
|---|---|---|---|---|---|---|---|
| A | Demo Journey Polish | Next-step CTAs, attach UX, empty states, copy | result components, `applications/[id]`, package/cover-letter/interview pages, `EmptyStatePage` | Coherent 1–2 click flow | LOW_FRONTEND_ONLY | — | `npm run lint && npm run build`; click-through each transition |
| B | Lightweight Learning Roadmap Shell | `/learning` route reusing `LearningRoadmap`; link from readiness | `app/learning/page.js`, nav/readiness links | Upskilling page exists | LOW_FRONTEND_ONLY | — | build; render with/without items |
| C | Help Assistant / Guided FAQ Shell | Static help drawer or `/help` explaining workflow ("what next?") | `app/help/page.js` or shared drawer, nav | Self-serve guidance, no LLM | LOW_FRONTEND_ONLY | — | build; open/close; links resolve |
| D | Demo Seed & E2E Sign-off Docs | Seed instructions, synthetic CV/JD scenarios, GA4 checklist, prod E2E checklist, sign-off | `docs/*` (extend checklist) | Repeatable demo + sign-off | LOW (docs) | — | `git diff --check` |
| E | Phase 6 Roadmap Doc | Marketplace, payment/credits, chatbot, academy, recruiter, analytics dashboard | `docs/phase6_product_scope.md` | Clear scope boundary | LOW (docs) | — | review |

Recommended order: **D → A → B → C → E** (lock demo data first, then polish, then shells, then scope).

---

## 3. Demo script (5–7 min) — strongest path

> Pre-seed (MF1) before presenting. Prefer the happy path; switch to panic path if AI is slow.

1. **Landing (`/`)** — *"AI CV Fit turns a CV + a job description into an action plan."* Click hero CTA. → `landing_cta_click`.
2. **Login (`/login`)** — sign in with demo account. → `login_success`.
3. **Dashboard / CV analysis (`/dashboard`)** — *"Upload CV, paste JD, choose strictness."* (If live: submit → `cv_analysis_submit`. If risky: open a pre-run result.)
4. **Result (`/dashboard` result)** — walk fit score, matched/missing skills, improvement plan. → `result_view`. Click **Download report** → `download_report_click`.
5. **Application (`/applications` → detail)** — open the pre-created application (pre-attached analysis). → `application_detail_view`.
6. **Interview (`…/interview`)** — show a question + the AI rubric feedback on the seeded answer. → `interview_start` (+ `interview_answer_submit_success` if you submit live).
7. **Cover letter (`…/cover-letter`)** — show the generated, editable letter; save a small edit. → `cover_letter_save_success`.
8. **Package/readiness (`…/package`)** — show fit score, readiness level, next actions.
9. **(Optional) Learning (`/learning`)** — show upskilling roadmap from the analysis gaps.
10. **GA4 Realtime** — show events landing live. *"Every step is instrumented for product analytics."*

**Avoid showing if unfinished:** job marketplace, pricing/payment, recruiter portal, real chatbot, camera interview.

### Panic demo path (AI slow/fails)
- Do **not** run a fresh analysis live.
- Open the **pre-created application** with a **pre-attached completed analysis**.
- Walk interview → cover letter → package using seeded content.
- Show GA4 Realtime events from navigation (`application_detail_view`, `result_view`, `language_switch`).
- Frame explicitly as *"production demo data"* — never fake numbers or capabilities.

---

## 4. Analytics funnel mapping

| Stage | Event(s) | What it proves | GA4 status | Missing |
|---|---|---|---|---|
| Acquisition | `landing_cta_click` | Landing intent | VERIFIED_IN_GA4 | — |
| Activation | `login_success`, `language_switch` | Auth + i18n usage | VERIFIED_IN_GA4 | — |
| Core analysis | `cv_analysis_submit` | Analysis started | CODED_NOT_YET_VERIFIED | — |
| Core analysis | `cv_analysis_success`, `result_view` | Analysis completed + viewed | NOT_TESTED_BECAUSE_REQUIRES_ANALYSIS | — |
| Core analysis | `cv_analysis_error` | Failure visibility | CODED_NOT_YET_VERIFIED | — |
| Core analysis | `download_report_click` | Report value | CODED_NOT_YET_VERIFIED | — |
| Workspace | `application_create_success`, `application_detail_view` | Application funnel | VERIFIED_IN_GA4 | — |
| Workspace | `attach_analysis_success` | Analysis linked | CODED_NOT_YET_VERIFIED | — |
| Profile | `profile_item_create_success` | Evidence building | CODED_NOT_YET_VERIFIED | — |
| Interview | `interview_start`, `interview_answer_submit_success` | Practice engagement | NOT_TESTED_BECAUSE_REQUIRES_ANALYSIS | — |
| Outputs | `package_generate_success` | Readiness output | NOT_TESTED_BECAUSE_REQUIRES_ANALYSIS | — |
| Outputs | `cover_letter_generate_success`, `cover_letter_save_success` | Cover letter value | NOT_TESTED_BECAUSE_REQUIRES_ANALYSIS | — |
| Retention | `logout_click` | Session end | CODED_NOT_YET_VERIFIED | — |

**Funnel coverage:** 18 events span acquisition → activation → core → workspace → outputs → retention.
**No funnel gaps identified for the core demo story.** Remaining `CODED_NOT_YET_VERIFIED` items just need a deployed E2E pass with synthetic data.
