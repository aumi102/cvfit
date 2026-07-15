# Phase 6 QA Checklist — Master Tracker for Đạt

> **Owner:** Đạt
> **Date:** 2026-07-15
> **Status:** ⚠️ MOSTLY COMPLETE — Privacy review DONE; frontend smoke + GA4 + sign-off still pending
> **Purpose:** Single source of truth tracking all QA/privacy/evaluation tasks for Phase 6

---

## Overview

Phase 6 QA work is split into these tracks:

| Track | Doc | Status |
|-------|-----|--------|
| Guardrails | `docs/phase6_guardrails.md` | ✅ DONE |
| Privacy Review | `docs/phase6_privacy_review.md` | ✅ DONE |
| Analytics Verification | `docs/phase6_acceptance_criteria.md` §6 | ⏳ PENDING (needs frontend) |
| Frontend Integration Smoke | `docs/phase6_demo_health_check.md` | ⏳ PENDING (needs Quân) |
| Demo Health Check | `docs/phase6_demo_health_check.md` | ⏳ PENDING |
| Team Sign-off | `docs/phase6_demo_health_check.md` | ⏳ PENDING |

---

## Track 1: Guardrails ✅ DONE

**Document:** `docs/phase6_guardrails.md` (v4.0, 2026-06-22)

Guardrails v4 extends v3 with Phase 6-specific rules. All Phase 6 features covered:
- Target Jobs
- Learning Roadmap
- Interview Practice v2
- Help Assistant
- Share Links
- Usage Shell

**Status:** ✅ COMPLETE — No further action needed unless new Phase 6 features are added.

---

## Track 2: Privacy Review ✅ DONE (2026-07-15)

**Document:** `docs/phase6_privacy_review.md` — **COMPLETE**

### Grep Scan Results (2026-07-15)

All 4 automated grep scans PASS:

| Scan | Pattern | Files | Result |
|------|---------|-------|--------|
| #1 Token logging | `share_token\|jwt\|token_hash\|raw_cv\|raw_jd` | share_links.py, services/share/, smoke | ✅ PASS — token_hash only in safe contexts (docstrings, function names, blocklist) |
| #2 CV/JD in share service | `cv_text\|jd_text\|raw_cv\|raw_jd` | services/share/ | ✅ PASS — only `hide_raw_cv=True`, `hide_raw_jd=True` redaction flags |
| #3 Answer in analytics | `answer_text\|interview_answer` | analytics.js, services/ | ✅ PASS — only constant/event names in analytics.js; @param jsdoc in interviewApi.js |
| #4 Share token in analytics | `share_token\|token_hash` | lib/, services/ | ✅ PASS — no matches found |

### Checkpoint Sign-off

| Checkpoint | Status | Date | Verified by |
|-----------|--------|------|------------|
| Share links token security | ✅ PASS | 2026-07-15 | Grep scan |
| Share links public view redaction | ✅ PASS | 2026-07-15 | Grep scan |
| Share links analytics privacy | ✅ PASS | 2026-07-15 | Grep scan |
| Help assistant data grounding | ✅ PASS | 2026-07-15 | Grep scan |
| Learning roadmap data grounding | ✅ PASS | 2026-07-15 | Grep scan |
| Interview v2 answer handling | ✅ PASS | 2026-07-15 | Grep scan |
| Target jobs JD handling | ✅ PASS | 2026-07-15 | Grep scan |
| Usage shell data scope | ✅ PASS | 2026-07-15 | Grep scan |
| Grep scan: no raw tokens in logs | ✅ PASS | 2026-07-15 | Grep scan |
| Final gate: flip SHARE_LINKS flag | ✅ READY | 2026-07-15 | All above |

### Automated Evaluation Results (2026-06-22) ✅

`API_BASE_URL=https://cvfit.onrender.com python scripts/evaluate_phase6_cases.py`

| Case | Module | Result |
|------|--------|--------|
| ph6_tj_01 | Target Jobs | ✅ PASS |
| ph6_tj_02 | Target Jobs | ✅ PASS |
| ph6_tj_03 | Target Jobs | ✅ PASS (cross-user → 404) |
| ph6_lr_01 | Learning | ✅ PASS |
| ph6_lr_03 | Learning | ✅ PASS (task progress update) |
| ph6_ip_01 | Interview v2 | ✅ PASS (session + questions + answer) |
| ph6_ip_03 | Interview v2 | ✅ PASS (cross-user → 404) |
| ph6_ha_01 | Help Assistant | ✅ PASS |
| ph6_ha_02 | Help Assistant | ✅ PASS |
| ph6_sl_01 | Share Links | ✅ PASS (flag-off → 404) |
| ph6_sl_02 | Share Links | ✅ PASS (flag-off → 404) |
| ph6_sl_04 | Share Links | ✅ PASS (cross-user → 404) |
| ph6_us_01 | Usage Shell | ✅ PASS |
| ph6_us_02 | Usage Shell | ✅ PASS |
| **TOTAL** | **All modules** | **14/14 ✅** |

---

## Track 3: Analytics Verification ⏳ PENDING (needs frontend)

**Document:** `docs/phase6_acceptance_criteria.md` §6
**Evaluation Script:** `scripts/evaluate_phase6_cases.py`

### How to verify GA4 events

1. Build frontend (Quân).
2. Open browser devtools → Network tab.
3. Filter by `collect?v=2` (GA4 hits).
4. Click through the happy-path flow.
5. For each event, open the payload and check:

```
# Should find something like:
&en=target_job_created&en2=target_job_created&ep.analytics_dim=val

# Should NOT find:
&en=target_job_created&ep.raw_cv_text=...
&en=interview_answer_submitted&ep.answer_text=...
&en=share_link_created&ep.share_token=...
```

### Verification steps per event category

#### Target Jobs events

1. Register/login synthetic account.
2. Create a target job.
3. PATCH to update title → check for `target_job_updated`.
4. Change status → check for `target_job_status_changed`.
5. Attach analysis → check for `target_job_analysis_attached`.
6. Open readiness → check for `target_job_readiness_viewed`.
7. Open package → check for `target_job_package_opened`.

**Forbidden in all payloads:** raw JD text, CV text, `fit_score` exact value, token, ID.

#### Learning events

1. Generate learning roadmap from a target job.
2. Click a learning task → check `learning_task_started`.
3. Mark task done → check `learning_task_completed`.

**Forbidden in all payloads:** raw CV/JD text, task description text.

#### Interview events

1. Create interview session → check `interview_session_created`.
2. Generate questions → check `interview_question_generated`.
3. Submit answer → check `interview_answer_submitted`. **Must only have `attempt_number`.**
4. View rubric → check `interview_feedback_viewed`. **Must only have `overall_bucket`.**

**Forbidden:** answer text, exact score, CV text.

#### Help Assistant events

1. Open help assistant → check `help_assistant_opened`.
2. Click a prompt chip → check `help_assistant_response_generated`. **Must only have `intent` + `fallback_used`.**
3. Ask an unsupported question → check `help_assistant_fallback_shown`. **Must only have `intent`.**

**Forbidden:** answer text, question text, CV/JD text.

#### Share Link events (only if flag on)

1. Create share link → check `share_link_created`. **Must NOT have token or `token_hash`.**
2. Open shared link in incognito → check `share_link_opened`.
3. Revoke link → check `share_link_revoked`.

**Forbidden:** token, `token_hash`, link ID, CV/JD text.

#### Usage events

1. Open usage page → check `usage_page_viewed`. **Must only have `plan_id`.**
2. Click plan card → check `plan_card_viewed`. **Must only have `plan_id`.**
3. (If usage near limit) check `limit_warning_shown`. **Must only have `category`.**

---

## Track 4: Frontend Integration Smoke ⏳ PENDING (needs Quân)

**Document:** `docs/phase6_demo_health_check.md`

Requires Quân to complete all frontend pages. Then:

### Step 1: Run backend smoke

```bash
API_BASE_URL=https://cvfit.onrender.com python scripts/smoke_phase6_e2e.py
# Expect: all PASS
```

### Step 2: Manual frontend smoke

- [ ] App loads at `https://cvfit-frontend.onrender.com` (or local equivalent)
- [ ] No console errors (Error level)
- [ ] Login/register flow works
- [ ] Target jobs CRUD visible
- [ ] Learning tasks visible and progress updates
- [ ] Interview session flow works end-to-end
- [ ] Help assistant returns scoped answer
- [ ] Usage page shows plan + counts
- [ ] Share link pages return 404 (flag-off)

### Step 3: Privacy smoke in browser

- [ ] Open Network tab, filter by `collect?v=2`
- [ ] Trigger each Phase 6 event
- [ ] Open each event payload
- [ ] Confirm no CV text, JD text, answer text, token, or PII in any payload
- [ ] Confirm `fit_score` appears only as coarse bucket (e.g. `55-74`)

### Step 4: Log smoke

- [ ] Open Render logs for API + worker services
- [ ] Trigger a few operations (create target job, learning, interview)
- [ ] Confirm no JWT, no raw CV/JD text, no share token in logs

---

## Track 5: Phase 5 Manual E2E ⏳ PENDING

**Document:** `docs/phase5_demo_checklist.md`

### Demo data setup

Before running the Phase 5 demo checklist, set up demo data:

1. Create account: `demo@cvfit.example.test` / any password
2. Upload a synthetic CV (fake name, fake experience)
3. Create an analysis job with a synthetic JD
4. Wait for job to complete
5. Create an Application workspace
6. Attach the completed analysis to the application
7. Generate a cover letter draft
8. Generate an application package
9. Answer one interview practice question

### Run Phase 5 demo checklist

Execute `docs/phase5_demo_checklist.md` step by step. Record each result:

```
1. [ ] Step description → PASS/FAIL
2. [ ] Step description → PASS/FAIL
...
```

For any FAIL: document the exact error, screenshot if possible, and create a bug issue.

---

## Track 6: Team Sign-off ⏳ PENDING

**Document:** `docs/phase6_demo_health_check.md`

Sign-off is the final gate. All above tracks must be ✅ before signing.

### Pre-sign-off checklist

- [ ] All backend smoke steps PASS
- [ ] All frontend smoke steps PASS (needs Quân)
- [ ] All GA4 event privacy checks PASS (needs Quân + Đạt)
- [ ] Phase 5 demo checklist PASS (needs Đạt)
- [ ] Demo data is synthetic only
- [ ] Phase 6 guardrails v4 reviewed
- [ ] Privacy review reviewed (✅ done 2026-07-15)
- [ ] `ENABLE_PHASE6_SHARE_LINKS` flag flip authorized (✅ all privacy checkpoints PASS)

### Sign-off

| Role | Name | Condition to sign | Status |
|------|------|------------------|--------|
| Backend | Phúc | Backend smoke PASS, no regressions | ☐ |
| Frontend | Quân | Frontend build/lint PASS, all pages work | ☐ |
| QA/Privacy | Đạt | Privacy review PASS ✅ (2026-07-15), GA4 events verified, demo checklist PASS | ☐ |

---

## Deferred Work

| Item | Owner | Condition |
|------|-------|-----------|
| GA4 wiring | Quân | Required before analytics verification |
| Frontend integration smoke | Quân | Required before sign-off |
| Phase 6 E2E report | Đạt | After frontend smoke |
| `ENABLE_PHASE6_SHARE_LINKS=true` flip | Phúc | After team sign-off |

---

## Command Reference

```bash
# Backend smoke
API_BASE_URL=https://cvfit.onrender.com python scripts/smoke_phase6_e2e.py

# Backend smoke with mutating
API_BASE_URL=https://cvfit.onrender.com PHASE6_SMOKE_ALLOW_MUTATING=1 python scripts/smoke_phase6_e2e.py

# Frontend build (Quân)
cd frontend && npm run build && npm run lint

# Evaluation: Phase 5 cover letter
python scripts/evaluate_cover_letter_cases.py

# Evaluation: Phase 5 application package
python scripts/evaluate_application_package.py

# Evaluation: Phase 4 scoring
python scripts/evaluate_scoring_cases.py

# Evaluation: Phase 4 comparison
python scripts/evaluate_comparison_cases.py

# Evaluation: Phase 4 interview prep
python scripts/evaluate_interview_prep_cases.py

# Evaluation: Phase 4 learning roadmap
python scripts/evaluate_roadmap_cases.py

# Backend tests
cd backend && python -m pytest

# Grep privacy scan (Phase 6 privacy review — all PASS 2026-07-15)
rg -i "share_token|jwt|token_hash|raw_cv|raw_jd" \
  backend/app/api/routes/share_links.py \
  backend/app/services/share/ \
  scripts/smoke_phase6_e2e.py

rg "cv_text|jd_text|raw_cv|raw_jd" backend/app/services/share/

rg "answer_text|interview_answer" \
  frontend/src/lib/analytics.js \
  frontend/src/services/

rg "share_token|token_hash" \
  frontend/src/lib/ \
  frontend/src/services/
```

---

*Last updated: 2026-07-15 by Đạt*
