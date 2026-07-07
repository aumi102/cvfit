# Phase 7 Plan — Controlled Payment Rollout & Final Demo Integrity

**Project:** AI CV Fit App  
**Current state:** PR #91 has been merged into `main` and is ready for deploy/retest.  
**Current verdict:** `MERGED_READY_FOR_DEPLOY_RETEST`  
**Important:** Phase 7 payment rollout must not begin until final production retest passes.

---

## 1. Phase 7 Goal

Phase 7 is no longer a broad feature-expansion phase. The goal is:

> Complete final demo-integrity fixes, verify production behavior with a fresh analysis, then roll out payment in a controlled and reversible way.

Phase 7 has two parts:

1. **Phase 7A — Final Demo Integrity Fixes**
   - Remove or replace fake marketing metrics.
   - Fix Learning task status update error.

2. **Phase 7B — Controlled Payment Rollout**
   - Enable billing carefully.
   - Verify checkout and webhook.
   - Only then consider credit gating.

---

## 2. Current Manual QA Status

| Section | Status | Notes |
|---|---:|---|
| Section 1 — Admin | PASS | Admin Analytics v2 renders; billing shows “Chưa bật”; no private content shown. |
| Section 2 — Pricing/Billing | PASS | Vietnamese plan names and correct prices; payment not live. |
| Section 3 — Learning + Vietnamese Result | MOSTLY PASS / 2 FIXES NEEDED | Vietnamese quality is acceptable after PR #91, but Learning detail status update fails. |
| Section 4 — Help Assistant | PASS | Acceptable. |
| Section 5 — Interview | PASS | Acceptable. |
| Section 6 — Cover Letter | PASS | Acceptable. |
| Section 7 — Application Package | PASS | Acceptable. |
| Section 8 — Final Flags | PASS | `ENABLE_BILLING=false`, `ENABLE_CREDIT_GATING=false`. |

---

## 3. Remaining Blockers Before Payment Rollout

### Blocker 1 — Fake Marketing Metrics Must Be Removed or Made Honest

Observed on frontend marketing/stat area:

- `10,000+` CV đã phân tích
- `98%` Độ chính xác AI
- `30s` Thời gian phân tích
- `4.9★` Đánh giá người dùng

These numbers must not be shown as real production metrics unless they are actually backed by real data.

#### Why this matters

This is a trust issue. The product is currently a demo/MVP, so fake scale or fake accuracy claims are not acceptable before payment rollout.

#### Acceptable fixes

Choose one of these approaches:

**Option A — Remove the stat bar entirely**
- Safest option.
- Good for MVP honesty.

**Option B — Replace with honest product-positioning copy**
Example:
- `Phân tích CV theo JD`
- `Gợi ý cải thiện có kiểm soát`
- `Lộ trình học tập cá nhân hóa`
- `Thanh toán đang thử nghiệm`

**Option C — Show only real metrics from backend/admin analytics**
Only if values are computed from real production data, for example:
- actual total analyses
- actual active users
- actual applications
- actual interview sessions

Do not show:
- fake user ratings
- fake AI accuracy
- fake “10,000+” scale
- fake speed claims unless measured

#### Acceptance criteria

- No unsupported `10,000+`, `98%`, `4.9★`, or similar fake claims remain in visible UI.
- Any displayed metric is either clearly product-positioning text or computed from real data.
- No fake metrics remain hidden in reusable frontend constants.
- Frontend lint/build pass.

---

### Blocker 2 — Learning Detail Status Update Fails

Observed on `/learning/<task_id>`:

- Changing task status shows error:
  - `Không thể cập nhật trạng thái.`

This must be fixed before Phase 7 payment rollout.

#### Expected behavior

On a Learning task detail page:

1. User changes status from dropdown.
2. Status update succeeds.
3. UI reflects the new status.
4. Refreshing the page preserves the new status.
5. Error message only appears if there is a real backend/API failure.

#### Likely areas to inspect

Frontend:
- `frontend/src/app/learning/[id]/page.js`
- `frontend/src/services/learningApi.js`
- Learning status dropdown component if separated

Backend:
- `backend/app/api/routes/learning.py`
- `backend/app/schemas/learning.py`
- Learning task model/status enum

Possible root causes:
- frontend sends wrong payload key
- frontend sends display label instead of enum value
- endpoint path mismatch
- backend status enum does not match frontend values
- PATCH response normalization issue
- ownership/auth handling issue
- stale task ID or wrong route param

#### Acceptance criteria

- Status update works on task detail page.
- Status update persists after refresh.
- Status values remain Vietnamese in UI but use safe backend enum values internally.
- No raw JSON or `undefined` appears.
- Error copy remains Vietnamese.
- Backend and frontend tests updated if practical.
- Frontend lint/build pass.
- Relevant backend tests pass.

---

## 4. Phase 7A Implementation PR

Create a focused PR before payment rollout.

### Branch

```bash
fix/phase7-demo-integrity-learning-status
```

### PR title

```text
fix: resolve phase 7 demo integrity blockers
```

### Commit message

```text
fix: resolve phase 7 demo integrity blockers
```

### Scope

Allowed:
- frontend marketing/stat area
- learning task detail status update
- learning API/service contract if needed
- backend learning route/schema if needed
- focused tests
- docs update

Not allowed:
- payment rollout
- enabling billing
- enabling credit gating
- payOS provider changes
- fake metrics
- unrelated UI redesign
- admin mutation endpoints

---

## 5. Phase 7A Validation Checklist

### Backend

```bash
python -m compileall backend/app
pytest backend/tests/test_phase6_learning.py
pytest backend/tests/test_vietnamese_generation.py
pytest backend/tests/test_vietnamese_analysis_pipeline.py
```

If test file names differ, run equivalent Learning and Vietnamese QA tests.

### Frontend

```bash
cd frontend
npm.cmd run lint
npm.cmd run build
cd ..
```

### Privacy / trust audit

Search changed files for:

```text
10,000
10000
98%
4.9
rating
accuracy
fake
mock
checkout_url
PAYOS
ENABLE_BILLING
ENABLE_CREDIT_GATING
AUTH_TOKEN
DATABASE_URL
eyJ
cv_text
jd_text
answer_text
```

Acceptance:
- No fake stats.
- No payment changes.
- No secrets.
- No raw private content.

---

## 6. Phase 7A Manual Retest

After merge + deploy:

1. Open public/landing/dashboard area where the fake stat bar appeared.
2. Confirm fake metrics are removed or replaced with honest copy.
3. Run a fresh CV analysis.
4. Open `/learning`.
5. Generate learning tasks from latest analysis if needed.
6. Open a task detail page.
7. Change status.
8. Confirm no `Không thể cập nhật trạng thái.` error.
9. Refresh page.
10. Confirm status persists.
11. Confirm Vietnamese generated result quality remains acceptable.
12. Confirm Sections 4–8 remain PASS.

### Phase 7A exit criteria

Phase 7A is complete only when:

```text
Fake metrics removed/replaced honestly
Learning status update works
Fresh analysis retest passes
Sections 1–8 pass
Payment flags still false
```

Then the product can be marked:

```text
READY_TO_START_PHASE_7_PAYMENT_ROLLOUT
```

---

## 7. Phase 7B — Controlled Payment Rollout

Only start after Phase 7A passes.

### 7B.1 Billing-only enablement

Set on Render backend only:

```env
ENABLE_BILLING=true
ENABLE_CREDIT_GATING=false
```

Do not enable credit gating yet.

Expected:
- users can open checkout
- payment page works
- existing free flows remain usable
- no credits are required yet

### 7B.2 Checkout smoke

Test:
- open `/pricing`
- choose a plan
- create checkout
- confirm checkout URL exists but do not expose it in logs/chat
- cancel flow returns safely
- no credits granted from cancel/success page alone

### 7B.3 Webhook verification

Test with one authorized payment only.

Expected:
- verified webhook grants credits
- duplicate webhook does not double-grant
- invalid signature does not grant credits
- order status updates correctly
- no raw webhook payload is logged to user-visible places

### 7B.4 Optional credit gating

Only after billing/webhook is verified:

```env
ENABLE_CREDIT_GATING=true
```

Expected:
- users with credits can use gated actions
- users without credits see Vietnamese upgrade/credit message
- existing generated artifacts remain accessible
- rollback is simple

---

## 8. Rollback Plan

If payment rollout has issues:

1. Disable gating first:

```env
ENABLE_CREDIT_GATING=false
```

2. If checkout/webhook is unstable, disable billing:

```env
ENABLE_BILLING=false
```

3. Redeploy backend.
4. Confirm free/demo flows still work.
5. Keep any paid order records; do not manually edit production payments unless absolutely necessary.

---

## 9. Team Responsibilities

### Phúc

- Own final decision to start Phase 7B.
- Deploy backend/frontend.
- Verify Render env flags.
- Run controlled payment smoke.
- Coordinate rollback if needed.

### Quân

- Remove/replace fake marketing metrics.
- Fix frontend Learning status update flow if frontend-side.
- Confirm Vietnamese UI copy.

### Đạt

- QA fake-metric removal.
- QA Learning status update persistence.
- QA privacy/no raw content.
- QA payment smoke and webhook behavior when Phase 7B starts.

---

## 10. Final Phase 7 Readiness Rule

Do not start payment rollout until all are true:

```text
PR #91 merged and deployed
Fresh analysis Vietnamese QA acceptable
Fake marketing metrics removed or made honest
Learning task status update fixed
Manual QA Sections 1–8 pass
ENABLE_BILLING=false before rollout
ENABLE_CREDIT_GATING=false before rollout
```

Only then begin controlled payment rollout.
