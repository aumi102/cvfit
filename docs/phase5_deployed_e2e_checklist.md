# Phase 5 Deployed E2E Checklist — AI CV Fit

> **Created:** 2026-06-17
> **Type:** Manual deployed end-to-end verification. **Synthetic data only.**
> **Status:** Phase 5 is **NOT** complete until this checklist passes on the deployed
> environment **and** the sign-off table below is filled. This doc does not declare completion.

---

## Environments

- **Frontend:** https://cvfit-frontend.onrender.com
- **Backend health:** https://cvfit.onrender.com/health (expect `{"status":"ok"}`)
- Run against the **deployed** build that includes the demo-journey polish PR.
- Use the synthetic demo account from `docs/phase5_demo_seed_data.md`. Do not paste credentials here.

---

## E2E steps

Mark each `[ ]` → `[x]` on demo prep day. If a step fails, note the issue and do not sign off.

| # | Step | Route / action | Expected result | Pass? |
|---|---|---|---|---|
| 1 | Backend health | `GET /health` | 200 `{"status":"ok"}` | [ ] |
| 2 | Landing loads | `/` | Landing renders, hero CTA visible | [ ] |
| 3 | Landing CTA | click hero CTA | Navigates to `/login`; `landing_cta_click` fires | [ ] |
| 4 | Login | `/login` | Auth succeeds → `/dashboard`; `login_success` fires | [ ] |
| 5 | Language switch | header toggle VI/EN | UI labels switch; `language_switch` fires | [ ] |
| 6 | CV analysis submit | `/dashboard` upload CV + JD → run | Job starts; `cv_analysis_submit` fires | [ ] |
| 7 | Result view | analysis completes | Result + score render; `cv_analysis_success`, `result_view` fire | [ ] |
| 8 | Download report | result → Download | DOCX downloads; `download_report_click` fires | [ ] |
| 9 | Create application | `/applications/new` | Created → detail; `application_create_success` fires | [ ] |
| 10 | Application detail view | `/applications/[id]` | Detail loads; `application_detail_view` fires | [ ] |
| 11 | Attach analysis | detail → pick recent analysis (or paste Job ID) | Attached; `attach_analysis_success` fires | [ ] |
| 12 | Profile item create | `/profile/evidence` → add item | Item appears; `profile_item_create_success` fires | [ ] |
| 13 | Interview load | `…/interview` | Questions load; `interview_start` fires | [ ] |
| 14 | Interview answer submit | answer a question | Rubric feedback shows; `interview_answer_submit_success` fires | [ ] |
| 15 | Cover letter generate | `…/cover-letter` → Generate | Letter renders; `cover_letter_generate_success` fires | [ ] |
| 16 | Cover letter save | edit + Save | Saved; `cover_letter_save_success` fires | [ ] |
| 17 | Package generate | `…/package` → Generate | Readiness renders; `package_generate_success` fires | [ ] |
| 18 | Learning shell | `/learning` | Loads, links resolve | [ ] |
| 19 | Help shell | `/help` | Loads, links resolve | [ ] |
| 20 | Logout | header → Logout | Returns to `/login`; `logout_click` fires | [ ] |

---

## GA4 Realtime events to verify

Confirm in GA4 Realtime (synthetic session). Already verified previously:
`language_switch`, `landing_cta_click`, `login_success`, `application_create_success`,
`application_detail_view`.

Verify the remaining during this run:
`cv_analysis_submit`, `cv_analysis_success`, `result_view`, `download_report_click`,
`attach_analysis_success`, `profile_item_create_success`, `interview_start`,
`interview_answer_submit_success`, `cover_letter_generate_success`,
`cover_letter_save_success`, `package_generate_success`, `logout_click`.

> Privacy: confirm events carry only safe params (feature_name, route, status, score_bucket,
> has_analysis, etc.). No CV/JD/answer/letter text, email, tokens, or IDs.

---

## Sign-off

Phase 5 may be declared complete **only** when all steps above pass on the deployed build and
all three owners sign off.

| Owner | Role | Verified | Date | Notes |
|---|---|---|---|---|
| Phúc | Frontend / integration | [ ] | | |
| Quân | Backend / API | [ ] | | |
| Đạt | QA / evaluation / guardrails | [ ] | | |

**Phase 5 status:** NOT COMPLETE until the table above is fully signed.
