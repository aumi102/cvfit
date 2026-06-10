# Phase 5 Team Plan — Application Readiness Suite

**Version:** 1.0
**Date:** 2026-06-10
**Status:** Active — Phase 5

---

## Phase 5 Objective

Transform AI CV Fit from a CV/JD scoring tool into a full career readiness workspace for students and fresh graduates. Users should be able to track applications, build a persistent evidence vault, generate application packages, practice interview answers, and see an honest readiness summary — all grounded in their real CV evidence.

---

## Product Direction

**Career Readiness Platform for Students and Freshers.**

Phase 5 takes the analysis engine built in Phases 1–4 and wraps it in a structured workspace that:

- Lets users track multiple job applications in one place.
- Stores career evidence persistently across sessions (skills, projects, certifications, achievements).
- Generates an application package (cover letter draft + readiness summary) from real CV evidence.
- Lets users practice typed interview answers and receive evidence-grounded feedback.
- Shows a readiness dashboard that is honest about gaps rather than inflating confidence.

All outputs remain evidence-first. No fabricated skills, no hiring guarantees.

---

## 7 Pillars

| # | Pillar | Owner (Phase 5) |
|---|---|---|
| 1 | Application Workspace | Phúc (backend), Quân (frontend) |
| 2 | Application Package Generator | Phúc (backend), Quân (frontend) |
| 3 | Cover Letter Draft v1 | Phúc (backend), Quân (frontend) |
| 4 | Interview Practice v2 | Phúc (backend), Quân (frontend) |
| 5 | Career Profile / Evidence Vault v1 | Phúc (backend), Quân (frontend) |
| 6 | Readiness Dashboard | Phúc (logic), Quân (frontend) |
| 7 | Demo & Release Hardening | Phúc (smoke/release docs), Đạt (QA/guardrails) |

---

## Scope

### Must-Have

- Application workspace CRUD (create/read/update/delete applications).
- Attach an existing analysis job to an application.
- Readiness summary per application derived from analysis result.
- Career profile CRUD (skills, projects, experience, education, certifications, achievements, links).
- Application package generation (stores payload as JSON; DOCX/PDF export is future work).
- Cover letter draft v1: evidence-grounded, clearly marked as draft, includes review notes.
- Interview practice v2: typed-answer flow with rubric scoring and evidence-grounded feedback.
- Guardrails v3 covering all Phase 5 output types.
- Demo-safe data: no real user PII in demo fixtures.
- Render smoke doc for Phase 5 endpoints.

### Should-Have

- Readiness dashboard page aggregating all application statuses.
- Empty/loading/error states for all new pages.
- Re-use existing analysis job/result/report structures wherever possible.

### Could-Have

- DOCX/PDF export for application package.
- Voice interview practice.
- AI cover letter revision flow.
- LinkedIn/ATS integration.

### Out of Scope (Phase 5)

- Real job board integrations.
- Recruiter-facing features.
- Multi-user collaboration.
- Automated job search.
- Payment/subscription gating.

---

## Team Assignment

### Phúc — Backend, Architecture, API Contracts

Owns:

- Backend architecture and data model design.
- Alembic migration plan (design in Phase 5; migration implemented in PR3).
- Application workspace backend (CRUD, attach-analysis, readiness endpoint).
- Career profile / evidence vault backend.
- Application package backend (generate, retrieve, download stub).
- Cover letter draft backend (LLM call + guardrails enforcement).
- Interview practice backend (question generation, answer submission, rubric scoring, feedback).
- Readiness summary logic.
- Render smoke and release docs.
- Backward compatibility with Phases 1–4 auth, history, result, report, and guest flows.

### Quân — Frontend

Owns:

- Application workspace UI: list, detail, new application flow.
- Career profile / evidence vault UI.
- Application package and cover letter UI.
- Interview practice UI: question display, typed answer, feedback display.
- Readiness dashboard.
- Loading, empty, and error states for all new pages.
- Compatibility with existing dashboard, history, and result pages.

### Đạt — Evaluation, Guardrails, QA

Owns:

- Guardrails v3 evaluation cases.
- Cover letter fabrication prevention cases.
- Interview feedback quality cases.
- Readiness summary honesty cases.
- Ownership/access control regression tests.
- Manual QA checklist for Phase 5 closeout.

---

## PR Sequence

| PR | Scope | Owner |
|---|---|---|
| PR1 | Contracts and docs only (this PR) | Phúc |
| PR2 | Evaluation skeleton and guardrail fixtures for Phase 5 | Đạt |
| PR3 | Backend application workspace + career profile APIs + Alembic migration | Phúc |
| PR4 | Frontend workspace + profile UI | Quân |
| PR5 | Application package + cover letter backend and frontend | Phúc, Quân |
| PR6 | Interview practice backend and frontend | Phúc, Quân |
| PR7 | QA/guardrails closeout, demo hardening, smoke docs | Đạt, Phúc |

---

## Definition of Done

Phase 5 is done when:

- Application workspace CRUD is live and scoped by user_id.
- Career profile items CRUD is live and scoped by user_id.
- Application package generation stores payload_json; download stub returns 200.
- Cover letter draft is evidence-grounded, includes review_notes, and never fabricates.
- Interview practice generates questions from JD/CV evidence, scores typed answers on rubric, returns feedback.
- Readiness summary is derived from analysis result and does not invent scores.
- Guardrails v3 covers all Phase 5 output types.
- All Phase 1–4 flows (auth, history, result v2/v3, report download, guest access_token) remain unbroken.
- No JWT, raw CV, storage path, or secret leaks in API responses, docs, or logs.
- Render smoke passes for at least the application workspace and career profile endpoints.
- Demo fixtures contain no real user PII.

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Cover letter draft fabricates skills not in CV | Enforce evidence-first input contract; guardrails v3 evaluation cases block merge |
| Interview feedback invents experience | Feedback must reference answer + evidence; missing evidence triggers "provide evidence" prompt |
| Readiness score inflates confidence | Readiness is derived from existing analysis result, not a new score; gaps are shown honestly |
| Application package exposes storage keys or raw CV | payload_json stores structured output only; no raw CV or internal paths |
| Phase 1–4 flows break due to new tables/routes | New tables are additive; new routes are under /v1/applications and /v1/profile (no overlap) |
| Demo data contains real PII | Demo fixtures use synthetic data only; Đạt verifies in QA checklist |
| Alembic migration fails on existing Render DB | Migration plan reviewed before PR3; dry-run checked locally before push |
| Frontend breaks existing dashboard on new pages | Quân adds new pages without modifying existing result/history routes |

---

## Validation Commands

```bash
# Check branch and file state
git status --short
git branch --show-current

# View contract diffs
git diff main -- docs/phase5_team_plan.md docs/application_workspace_contract.md \
  docs/interview_practice_contract.md docs/cover_letter_guardrails.md docs/guardrails_v3.md

# Confirm no backend/frontend files changed
git diff main --name-only | grep -v "^docs/"
```

Expected: only docs/ files changed in PR1.
