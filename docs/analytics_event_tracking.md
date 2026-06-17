# Analytics Event Tracking

## Current setup

- GTM container: `GTM-W3QFT8W3`
- GA4 Measurement ID: `G-CBYM61HFV8`
- Base `page_view` tracking is handled by the Google tag in GTM (published on All Pages).
- GTM is loaded via `NEXT_PUBLIC_GTM_ID` (see `frontend/.env.example`); no GA4 Measurement ID is hardcoded in the frontend.

## Frontend custom events

All custom events are pushed to `window.dataLayer` via the helper
`frontend/src/lib/analytics.js` (`trackEvent(name, params)`). The helper:

- no-ops on the server and when `dataLayer`/GTM is unavailable (e.g. ad blocker);
- enforces GA4-compatible event names;
- runs every param through an allow-list, dropping anything not whitelisted;
- truncates string values to 100 chars and auto-attaches the current `route` (pathname only).

| Event | When fired | Safe params |
|---|---|---|
| landing_cta_click | landing hero CTA click | feature_name, source, route |
| login_success | login success | feature_name, route |
| logout_click | logout click | feature_name, route |
| language_switch | language changed | feature_name, language, route |
| cv_analysis_submit | CV analysis submitted | feature_name, route |
| cv_analysis_success | CV analysis result loaded | feature_name, status, score_bucket, route |
| cv_analysis_error | CV analysis failed | feature_name, status, error_type, status_code, route |
| result_view | result dashboard viewed | feature_name, score_bucket, route |
| download_report_click | report download clicked | feature_name, route |
| application_create_success | application created | feature_name, application_status, has_analysis, route |
| application_detail_view | application detail viewed | feature_name, application_status, has_analysis, route |
| attach_analysis_success | analysis attached | feature_name, has_analysis, route |
| profile_item_create_success | evidence item created | feature_name, item_type, route |
| interview_start | interview questions loaded | feature_name, route |
| interview_answer_submit_success | answer submitted & scored | feature_name, route |
| package_generate_success | package generated | feature_name, has_analysis, route |
| cover_letter_generate_success | cover letter generated | feature_name, has_analysis, route |
| cover_letter_save_success | cover letter saved | feature_name, has_analysis, route |

### score_bucket values

The raw fit score never leaves the browser — it is bucketed before sending:

```
0_20
20_40
40_60
60_80
80_100
unknown
```

## Privacy rules

Never send:

- CV text
- JD text
- interview questions or answers
- cover letter text (generated text, section text, review notes)
- profile/evidence text (title, description, skills, tags)
- raw email
- access token / JWT
- S3 / storage keys
- database IDs
- full UUIDs (application ID, job ID, analysis job ID)
- raw API response bodies

Only low-cardinality, non-identifying metadata is forwarded. The param
allow-list in `analytics.js` (`feature_name`, `route`, `status`, `status_code`,
`error_type`, `item_type`, `interview_type`, `application_status`,
`has_analysis`, `score_bucket`, `language`, `source`) is the enforced boundary.

## GTM setup required after deploy

1. In GTM, create Custom Event triggers whose event names match the events above.
2. Create one GA4 Event tag (or per-event GA4 Event tags) firing on those triggers.
3. Forward only the safe params listed above to GA4.
4. Publish the GTM workspace.
5. Verify in Tag Assistant and GA4 Realtime.
