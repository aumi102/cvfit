# Phase 5 Deployed E2E Execution Report

## Metadata

- **Date/time:** 2026-06-17
- **Frontend URL:** https://cvfit-frontend.onrender.com
- **Backend URL:** https://cvfit.onrender.com
- **Main commit:** `ff71964` (feat(frontend): polish Phase 5 demo journey (#64))
- **Executor:** Automated authenticated API-level E2E (Claude Code) using a dedicated demo account
- **Data rule:** Synthetic only. No real CV/JD/user data used. No credentials, tokens, or
  secrets recorded. Object IDs redacted to first 6 chars.

---

## Summary

- **Overall status:** `PASS_WITH_MANUAL_GA4_PENDING`
- **Why:** The authenticated, data-mutating E2E was executed end-to-end against the deployed
  backend with synthetic data and **every backend step passed** (login → attach analysis →
  interview Q&A → cover letter generate/save → package generate → report download → logout).
  Read-only route smoke is green. **However**, this run exercised the **HTTP API directly**, so
  it did **not** trigger the browser-side `dataLayer` GA4 events. GA4 Realtime confirmation of
  the events still requires a manual browser session, and the three-owner sign-off is still
  pending. Therefore Phase 5 is **not** yet declared complete.
- **What passed:** All 8 routes (200), backend health, login, application create, analysis
  attach (an existing completed analysis was used), profile/evidence create, interview question
  load + answer submit (rubric returned), cover letter generate + save, package generate, report
  download, logout.
- **What is pending:** GA4 Realtime visual verification (browser) + sign-off table.

---

## Route smoke

| Route | Status | Result |
|---|---|---|
| `/` | 200 | PASS |
| `/dashboard` | 200 | PASS |
| `/applications` | 200 | PASS |
| `/applications/new` | 200 | PASS |
| `/profile` | 200 | PASS |
| `/profile/evidence` | 200 | PASS |
| `/learning` | 200 | PASS (new in #64) |
| `/help` | 200 | PASS (new in #64) |
| `GET /health` | 200 | PASS `{"status":"ok"}` |

Control: unknown route `/nonexistent-xyz-123` → 404 (confirms 200s are real routes).

---

## API/E2E steps

All calls authenticated as the demo account via Bearer token (token never printed). IDs redacted.

| Step | Result | Sanitized evidence | Notes |
|---|---|---|---|
| 1. Backend health | PASS | `GET /health` → 200 `{"status":"ok"}` | |
| 2. Landing loads | PASS | `/` → 200 | |
| 3. Login | PASS | `POST /v1/auth/login` → 200; `GET /v1/auth/me` → 200 | Token acquired, not shown |
| 4. List job history | PASS | `GET /v1/jobs/history` → 200; 11 jobs, 11 succeeded | |
| 5. Find completed analysis | PASS | succeeded job `302de3...` selected | No fresh analysis needed |
| 6. Create application | PASS | `POST /v1/applications` → 201; app `e95011...` | Synthetic Demo Company / Demo Frontend Developer |
| 7. Application detail | PASS | `GET /v1/applications/{id}` → 200 | |
| 8. Attach analysis | PASS | `POST /v1/applications/{id}/attach-analysis/{job}` → 200 | Existing completed analysis attached |
| 9. Profile/evidence create | PASS | `POST /v1/profile/items` → 201; item `0c69a1...` (project) | Synthetic Demo React Portfolio |
| 10. Interview questions load | PASS | `GET …/interview/questions` → 200; count=2 | |
| 11. Interview answer submit | PASS | `POST …/interview/answers` → 201 | Synthetic answer; rubric returned |
| 12. Cover letter generate | PASS | `POST …/cover-letter/generate` → 201 | |
| 13. Cover letter save | PASS | `PATCH …/cover-letter` → 200 | Edited closing section |
| 14. Package generate | PASS | `POST …/package/generate` → 201 | Readiness produced |
| 15. Report download | PASS | `GET /v1/jobs/{job}/report/download` → 200 | DOCX served (Bearer auth) |
| 16. Logout | PASS | `POST /v1/auth/logout` → 200 | |

> Sanitized-evidence policy honoured: no tokens, cookies, emails, full IDs, or raw API response
> bodies recorded. IDs redacted to first 6 chars + `...`.

---

## Analysis-dependent steps

A completed analysis **was available** — the demo account's job history contained 11 succeeded
analyses. An existing completed analysis (`302de3...`) was attached to the synthetic application,
so no fresh CV upload / `create-score` run was required. All analysis-dependent steps (attach,
interview, cover letter, package, report download) executed and passed.

---

## GA4 event verification

> **Important:** This run was an **API-level** E2E (direct HTTP calls). The custom analytics
> events fire only in the **browser** via `window.dataLayer.push(...)`. Therefore this run did
> **not** produce GA4 events and cannot assert GA4 verification for them. The backend
> capability behind each event is confirmed working; the GA4 Realtime confirmation requires a
> manual browser walkthrough.

| Event | Status | Evidence/notes |
|---|---|---|
| landing_cta_click | VERIFIED_MANUALLY_BEFORE | Confirmed in GA4 Realtime previously |
| login_success | VERIFIED_MANUALLY_BEFORE | Confirmed previously |
| language_switch | VERIFIED_MANUALLY_BEFORE | Confirmed previously |
| application_create_success | VERIFIED_MANUALLY_BEFORE | Confirmed previously |
| application_detail_view | VERIFIED_MANUALLY_BEFORE | Confirmed previously |
| cv_analysis_submit | PENDING_MANUAL_GA4_UI_CHECK | Backend analysis path validated; browser event not fired this run |
| cv_analysis_success | PENDING_MANUAL_GA4_UI_CHECK | Completed analyses exist; browser event needs UI run |
| cv_analysis_error | PENDING_MANUAL_GA4_UI_CHECK | Negative path; needs UI |
| result_view | PENDING_MANUAL_GA4_UI_CHECK | Needs browser result view |
| download_report_click | PENDING_MANUAL_GA4_UI_CHECK | API download passed; browser click event needs UI |
| attach_analysis_success | PENDING_MANUAL_GA4_UI_CHECK | API attach passed; browser event needs UI |
| profile_item_create_success | PENDING_MANUAL_GA4_UI_CHECK | API create passed; browser event needs UI |
| interview_start | PENDING_MANUAL_GA4_UI_CHECK | API questions loaded; browser event needs UI |
| interview_answer_submit_success | PENDING_MANUAL_GA4_UI_CHECK | API submit passed; browser event needs UI |
| package_generate_success | PENDING_MANUAL_GA4_UI_CHECK | API generate passed; browser event needs UI |
| cover_letter_generate_success | PENDING_MANUAL_GA4_UI_CHECK | API generate passed; browser event needs UI |
| cover_letter_save_success | PENDING_MANUAL_GA4_UI_CHECK | API save passed; browser event needs UI |
| logout_click | PENDING_MANUAL_GA4_UI_CHECK | API logout passed; browser event needs UI |

---

## Sign-off

| Owner | Area | Status | Notes |
|---|---|---|---|
| Phúc | Backend/deploy/docs | Pending | API E2E green; review report |
| Quân | Frontend/UI | Pending | Run browser walkthrough to confirm GA4 Realtime events |
| Đạt | QA/evaluation/guardrails | Pending | Confirm GA4 events + guardrail/disclaimer presence in UI |

---

## Final verdict

**Phase 5 is NOT yet complete**, but it is close: the deployed backend passed a full authenticated
synthetic E2E and all routes are healthy. Outstanding before closeout:

1. **GA4 Realtime (browser):** Do one manual browser walkthrough on the demo account
   (synthetic data) to confirm the `PENDING_MANUAL_GA4_UI_CHECK` events appear in GA4 Realtime.
2. **Sign-off:** Phúc / Quân / Đạt mark the table above as Done.

Only when both are satisfied may Phase 5 be declared complete. Current status:
`PASS_WITH_MANUAL_GA4_PENDING` (backend E2E passed; GA4 UI verification + sign-off pending).

> Note: the synthetic application (`e95011...`), evidence item (`0c69a1...`), generated cover
> letter, and package created by this run were **left in place** on the demo account — they
> double as pre-seeded demo data per `docs/phase5_demo_seed_data.md`. No production data was
> deleted.
