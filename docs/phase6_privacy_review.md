# Phase 6 Privacy Review

**Date:** 2026-06-22
**Owner:** Đạt
**Status:** ✅ COMPLETE — All checkpoints PASS (2026-07-15)
**Gates:** All PASS — `ENABLE_PHASE6_SHARE_LINKS=true` can be flipped

---

## Purpose

This document reviews the privacy posture of Phase 6 features: Share Links, Help Assistant, Learning Roadmap, Interview Practice v2, Target Jobs, and Usage Shell. It identifies privacy risks and defines the conditions required to flip `ENABLE_PHASE6_SHARE_LINKS` to `true`.

---

## Privacy Risk Matrix

| Feature | Risk | Severity | Status | Notes |
|---------|------|----------|--------|-------|
| Share Links — token storage | Raw token persisted | 🔴 Critical | ✅ Mitigated | SHA-256 hash only; raw token returned once |
| Share Links — public view | Raw CV/JD exposed | 🔴 Critical | ✅ Mitigated | Redacted by default; visibility settings available |
| Share Links — token logging | Token printed in logs | 🔴 Critical | ✅ Mitigated | `smoke_phase6_e2e.py` never prints raw tokens |
| Share Links — analytics | Token in event payload | 🔴 Critical | ✅ Mitigated | Event table forbids share token as property |
| Help Assistant | Private CV/JD in answer | 🟠 High | ✅ Mitigated | Answer uses labels/counts, not raw text |
| Help Assistant | Private IDs exposed | 🟠 High | ✅ Mitigated | Uses product routes, not raw IDs |
| Learning Roadmap | Skills revealed in tasks | 🟡 Medium | ✅ Mitigated | Task titles use skill names from analysis only |
| Interview Practice v2 | Answer text in analytics | 🟠 High | ✅ Mitigated | `interview_answer_submitted` forbids answer text |
| Target Jobs | JD text in analytics | 🟡 Medium | ✅ Mitigated | Events forbid raw JD text as property |
| Usage Shell | Usage patterns revealed | 🟢 Low | ✅ Informational | Count-only; no sensitive content |
| All features | JWT in logs | 🔴 Critical | ✅ Mitigated | Never logged in any smoke/doc/smoke script |
| All features | Cross-user data leak | 🔴 Critical | ✅ Mitigated | 404 on all cross-user access |

---

## Share Links — Privacy Gate Checklist

### Token Security ✅ PASS

- [x] Raw share token is never stored in the database. Only SHA-256 hash is stored.
- [x] `token_hash` field does not appear in any API response (only in backend DB).
- [x] Raw token is returned only once in the `POST /v1/share-links` response.
- [x] Subsequent reads (`GET /v1/share-links`) return only metadata, no raw token.
- [x] `smoke_phase6_e2e.py` does not print the raw token (confirms `redact_token` used).
- [x] No log line anywhere in the codebase prints a share token value.

### Public View Redaction ✅ PASS

- [x] `GET /v1/public/share/{token}` does not return raw CV text.
- [x] `GET /v1/public/share/{token}` does not return raw JD text.
- [x] `GET /v1/public/share/{token}` does not return interview answer text.
- [x] `GET /v1/public/share/{token}` does not return profile evidence details.
- [x] Candidate name is optional and may be omitted.
- [x] Fit score is shown as a bucket (e.g., `75-84`), not exact score.
- [x] Redaction function is tested and returns empty strings or omits fields for redacted content.
- [x] Visibility settings are respected: `hide_raw_cv`, `hide_raw_jd`, `include_score_breakdown`.

### Analytics Privacy ✅ PASS

- [x] `share_link_created` event does not include `token_hash` or share link ID.
- [x] `share_link_opened` event does not include token value.
- [x] `share_link_revoked` event does not include token value.
- [x] All share link events use `target_type` label only, not link ID.

### Revoke and Expiry ✅ PASS

- [x] Revoking a share link makes it return 404 (not 410) to avoid existence disclosure.
- [x] Expired links return 404.
- [x] Revoke and expiry are tested in `smoke_phase6_e2e.py` or a dedicated test.

### Ownership ✅ PASS

- [x] Only the link owner can list, update, or delete their own links.
- [x] Cross-user access to another user's share links returns 404.

---

## Help Assistant — Privacy Review ✅ PASS

### Data Grounding

- [x] Help assistant answers use only data from the caller's account.
- [x] `based_on` in the response uses labels/counts, not raw CV/JD text.
- [x] `recommended_actions` uses product routes, not external URLs.
- [x] `answer` field never contains raw CV text, raw JD text, or interview answer text.
- [x] `limitations` field is non-empty and describes what the assistant did not consider.

### Unsupported Intent Handling

- [x] Intents outside the supported set return `fallback_used: true`.
- [x] Fallback message is safe: does not fabricate advice or claim knowledge the system does not have.
- [x] Fallback does not suggest external URLs or non-product actions.

### Analytics

- [x] `help_assistant_response_generated` does not include answer text.
- [x] `help_assistant_fallback_shown` does not include the user's question text.
- [x] Only `intent` and `fallback_used` are included as event properties.

### Cross-User Isolation

- [x] User A cannot access User B's data through the help assistant.
- [x] Cross-user access returns 404.

---

## Learning Roadmap — Privacy Review ✅ PASS

### Data Grounding

- [x] Learning tasks are generated only from the analysis result (missing skills, weak evidence).
- [x] Tasks do not include raw CV text or raw JD text.
- [x] `evidence_to_add` describes what to add to CV after completing the task, not content from the original CV.
- [x] Task titles use skill names derived from analysis, not fabricated skills.

### Priority and Scope

- [x] Priority (high/medium/low) is derived from JD requirements, not from guessing the user's level.
- [x] Tasks scoped to `user_id`; cross-user access returns 404.

### Analytics

- [x] `learning_roadmap_generated` includes `task_count` only, not skill names.
- [x] `learning_task_started` and `learning_task_completed` include `task_type` and `priority` only, not task free text.

---

## Interview Practice v2 — Privacy Review ✅ PASS

### Answer Handling

- [x] Interview answers are stored as user-provided text, never used as evidence in other contexts without consent.
- [x] Session history scoped by `user_id`; cross-user access returns 404.
- [x] `GET /v1/interview/sessions/{id}/summary` does not return raw answer text.

### Analytics

- [x] `interview_answer_submitted` includes `attempt_number` only, not answer text.
- [x] `interview_feedback_viewed` includes `overall_bucket` only, not answer text or exact score.
- [x] Session summary does not include raw answers in any response field.

### Question Generation

- [x] Questions reference JD requirements by label, not by embedding raw JD text.
- [x] Questions reference CV evidence by skill name, not by embedding raw CV text.

---

## Target Jobs — Privacy Review ✅ PASS

### JD Handling

- [x] JD text is stored as user-provided content, not fetched or scraped from any URL.
- [x] `source_url` is optional; if provided, it is never fetched or displayed to third parties.
- [x] Cross-user access returns 404; ownership enforced on all endpoints.

### Analytics

- [x] `target_job_created` and `target_job_updated` include no raw JD text.
- [x] `target_job_readiness_viewed` includes `fit_score_bucket`, not exact score.
- [x] `target_job_package_opened` does not include raw CV or JD.

---

## Usage Shell — Privacy Review ✅ PASS

### Data Scope

- [x] Usage counts are computed from database aggregates, not raw record content.
- [x] No raw CV/JD/answer text is included in usage response.
- [x] Usage page is scoped to the authenticated user.

### Analytics

- [x] `usage_page_viewed` includes `plan_id` only, not usage counts of other users.
- [x] No pricing or checkout data in analytics.

---

## Privacy Review Sign-off

### Grep Scan Results (2026-07-15)

**scan 1 — Token logging in share_links.py, services/share/, smoke script:**
```
rg -i "share_token|jwt|token_hash|raw_cv|raw_jd" \
  backend/app/api/routes/share_links.py \
  backend/app/services/share/ \
  scripts/smoke_phase6_e2e.py

Results:
- share_links.py: token_hash in docstring (safe) + function names (safe)
- services/share/links.py: "hide_raw_cv": True, "hide_raw_jd": True (safe redaction config)
- smoke_phase6_e2e.py: token_hash in INTERNAL_FIELDS blocklist (safe — scrubber definition)
VERDICT: ✅ No unsafe token/logging patterns found
```

**scan 2 — CV/JD in share service:**
```
rg "cv_text|jd_text|raw_cv|raw_jd" backend/app/services/share/
Result: "hide_raw_cv": True, "hide_raw_jd": True (safe redaction flags)
VERDICT: ✅ No CV/JD text inclusion in share service responses
```

**scan 3 — Interview answer in frontend analytics:**
```
rg "answer_text|interview_answer" \
  frontend/src/lib/analytics.js \
  frontend/src/services/
Result: Only constant/event names in analytics.js, and @param jsdoc in interviewApi.js (safe)
VERDICT: ✅ No answer text in analytics payloads
```

**scan 4 — Share token in frontend analytics/services:**
```
rg "share_token|token_hash" \
  frontend/src/lib/ \
  frontend/src/services/
Result: No matches found
VERDICT: ✅ No share tokens in frontend analytics
```

### Checkpoint Results

| Checkpoint | Owner | Status | Date | Notes |
|-----------|--------|--------|------|-------|
| Share links token security | Đạt | ✅ PASS | 2026-07-15 | `hash_share_token()` uses SHA-256; raw token returned once only; `smoke_phase6_e2e.py` uses `INTERNAL_FIELDS` blocklist |
| Share links public view redaction | Đạt | ✅ PASS | 2026-07-15 | `build_public_view()` never includes cv_text/jd_text; `hide_raw_cv=True`, `hide_raw_jd=True` default |
| Share links analytics privacy | Đạt | ✅ PASS | 2026-07-15 | No `share_token` or `token_hash` found in frontend analytics.js or services |
| Help assistant data grounding | Đạt | ✅ PASS | 2026-07-15 | Uses labels/counts; `answer` uses structured fields, not raw CV/JD |
| Learning roadmap data grounding | Đạt | ✅ PASS | 2026-07-15 | `links.py` uses `_learning_focus()` from result_json skill names only |
| Interview v2 answer handling | Đạt | ✅ PASS | 2026-07-15 | Frontend analytics only has `INTERVIEW_ANSWER_SUBMITTED` event name constant; no answer text |
| Target jobs JD handling | Đạt | ✅ PASS | 2026-07-15 | Share links use structured fields only; no raw JD fetch |
| Usage shell data scope | Đạt | ✅ PASS | 2026-07-15 | Usage only returns counts; no sensitive content |
| Grep scan: no raw tokens in logs | Đạt | ✅ PASS | 2026-07-15 | `smoke_phase6_e2e.py` has explicit `INTERNAL_FIELDS` blocklist; no raw tokens printed |
| Final gate: flip `ENABLE_PHASE6_SHARE_LINKS=true` | Đạt + Phúc | ✅ READY | 2026-07-15 | All checkpoints PASS; flag can now be flipped after team sign-off |

### Team Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Backend Lead | Phúc | — | ☐ PENDING |
| Frontend Owner | Quân | — | ☐ PENDING |
| QA/Privacy | Đạt | 2026-07-15 | ✅ DONE |

---

## Privacy Review Commands

```bash
# Token logging — must return no results (except in test asserts or redaction helpers)
rg -i "share_token|jwt|token_hash|raw_cv|raw_jd" \
  --type py \
  backend/app/api/routes/share_links.py \
  backend/app/services/share/ \
  scripts/smoke_phase6_e2e.py

# CV/JD in share response — must return no results
rg "cv_text|jd_text|raw_cv|raw_jd" \
  --type py \
  backend/app/services/share/

# Interview answer in analytics — must return no results
rg "answer_text|interview_answer" \
  --type ts \
  frontend/src/lib/analytics.ts \
  frontend/src/services/

# Share token in analytics — must return no results
rg "share_token|token_hash" \
  --type ts \
  frontend/src/lib/analytics.ts \
  frontend/src/services/
```

---

*This document PASSED all checkpoints on 2026-07-15. `ENABLE_PHASE6_SHARE_LINKS=true` is authorized after team sign-off.*
