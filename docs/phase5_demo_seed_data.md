# Phase 5 Demo Seed Data — AI CV Fit

> **Created:** 2026-06-17
> **Type:** Runbook. No code. **Synthetic data only.**
> **Status:** Phase 5 is **NOT** complete. This doc prepares demo data; closeout still
> requires the deployed E2E run (`docs/phase5_deployed_e2e_checklist.md`) + team sign-off.

---

## 1. Hard rules

- **Synthetic only.** Never use a real candidate's CV, JD, email, or answers in a demo.
- **No committed credentials.** Do not put the demo account email/password (or any token, JWT,
  S3 key, DB URL) in this repo, in docs, or in screenshots. Store them in the team's private
  password manager only.
- **No fabricated results.** Use the real product to generate analysis/cover-letter/package
  outputs from synthetic inputs. Do not hand-edit numbers to look better.
- **Cross-reference:** see `docs/jobready_benchmark_gap_audit.md` and
  `docs/phase5_demo_readiness_plan.md` for the demo journey rationale.

---

## 2. Demo account

- Create **one** dedicated demo account via the normal `/register` flow.
- Use a clearly synthetic identity, e.g. full name `Demo Candidate`, a team-owned mailbox alias.
- Keep credentials in the private password manager. Reference them in the demo as
  "the demo account" — never read them aloud or show them on screen.

---

## 3. Pre-created objects (seed before demo day)

Create these by **using the product** so every screen has real content instantly:

| # | Object | How | Why |
|---|---|---|---|
| 1 | One completed analysis job | `/dashboard` → upload synthetic CV + paste synthetic JD → run | Backs result view, attach, score bucket |
| 2 | One application with attached analysis | `/applications/new` → create → open → attach the analysis (picker) | Unlocks interview/cover-letter/package |
| 3 | One profile/evidence item | `/profile/evidence` → add a Skill or Project | Shows evidence vault populated |
| 4 | One generated cover letter | application → Cover Letter → Generate | Shows AI writing output |
| 5 | One package/readiness result | application → Package → Generate | Shows readiness summary + next actions |
| 6 | One submitted interview answer | application → Interview → answer one question | Shows rubric feedback + history |

---

## 4. Synthetic application fields (example)

Use evergreen, fictional values — adapt freely, keep them obviously synthetic:

```text
Company name: Northwind Labs (fictional)
Role title:   Frontend Engineer
JD (synthetic, paste a short version like):
  We are hiring a Frontend Engineer to build accessible React/Next.js interfaces.
  Required: JavaScript, React, REST APIs, Git, responsive CSS.
  Nice to have: TypeScript, testing, performance optimisation, basic analytics.
```

Use a **synthetic CV** (a fictional résumé you control) — never a real person's document.

---

## 5. Panic path (if live AI generation is slow or fails)

Do **not** run a fresh analysis live under time pressure. Instead:

1. Open the **pre-created application** (object #2) that already has an attached analysis.
2. Walk **Interview → Cover Letter → Package** using the seeded outputs (objects #4–#6).
3. Show **GA4 Realtime** events from navigation (`application_detail_view`, `result_view`,
   `language_switch`).
4. Frame it explicitly as *"production demo data"* — never present fabricated numbers or claim
   capabilities the product does not have.

---

## 6. Do NOT show in the demo

Job marketplace/search, pricing/credits/payment, recruiter portal, real chatbot/LLM assistant,
course marketplace, video/camera interview. These are Phase 6 (see `docs/phase6_product_scope.md`).
