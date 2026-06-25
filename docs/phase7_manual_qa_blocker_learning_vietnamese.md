# Pre-Phase-7 Manual QA — Learning + Vietnamese Blocker

Records the manual production QA progress and the fix for the Section 3 (Learning)
blocker plus the most-visible Vietnamese result-page copy. Payment remains paused
(`ENABLE_BILLING=false`, `ENABLE_CREDIT_GATING=false`).

## Manual QA progress

| Section | Result |
| --- | --- |
| 1. Admin | **PASS** — admin dashboard + Analytics v2 (funnel, 7/30-day, depth, billing readiness) render; billing "Chưa bật"; no private content. |
| 2. Pricing/Billing | **PASS** — VI plan names ("Gói khởi đầu", "Gói demo Pro"), prices 20.000đ / 49.000đ; `/billing` safe, not implying live payment. |
| 3. Learning | **BLOCKED before this PR** → fixed here (retest required after deploy). |
| 4–8 | Not yet reached (resume after retest). |

## Root cause (Section 3 — Learning)

- CV analysis writes a `learning_roadmap` array **inside** `result_json` (via the
  result_v3 assembly) but does **not** persist `LearningTask` rows.
- `LearningTask` rows are created **only** by a generate endpoint
  (`POST /v1/learning/roadmaps/generate` or the target-job variant).
- `/learning` lists `LearningTask` rows, so after a fresh analysis it was empty —
  and its empty state told the user to "Chạy phân tích CV" (analyze again), which
  is wrong when the user just analyzed.
- Additionally, several analysis-result strings are generated deterministically in
  English (`result_v2`/`result_v3` + interview-prep/roadmap generators), so they
  showed in English even in VI mode (score labels, explanations, interview-prep
  questions, roadmap text).

## Fix summary (this PR)

**Learning (the blocker):**
- `/learning` empty state now checks for the user's latest **succeeded** analysis
  (via the existing `GET /v1/jobs/history` — safe metadata only). If one exists, it
  shows a Vietnamese CTA **"Tạo lộ trình học tập từ phân tích gần nhất"** that calls
  `POST /v1/learning/roadmaps/generate` with that `analysis_job_id` and
  `language=vi`, then reloads the task list. If there is genuinely no analysis, the
  original "Chạy phân tích CV" CTA remains. No raw "Not Found" is ever shown.
- The learning-task generator (`generate_learning_tasks`) gained an optional
  `language` param (default `en`); with `vi` the task title/description/evidence
  prose is Vietnamese (skill/tech names preserved). Threaded through the generate
  endpoint via `RoadmapGenerateRequest.language`.

**Vietnamese result copy (fixed deterministic strings):**
- A frontend map (`utils/resultI18n.js`) localizes the **score-breakdown labels**
  (Mức độ khớp kỹ năng / Mức độ khớp trách nhiệm / Mức kinh nghiệm / Mức độ liên
  quan dự án / Chất lượng CV), their **explanations**, and the **limitation
  disclaimers**, applied in `ResultCardV2.jsx`. Backend response contract unchanged.

## Out of scope (documented)

- **Interpolated** result prose — the summary, missing-skill reasons/suggestions,
  improvement actions, interview-prep questions, and roadmap detail — is generated
  by the backend analysis pipeline with skill/JD values inlined. Localizing it
  requires threading a `language` through that pipeline (and risks many phase-3
  result tests). It is a **follow-up**; new analyses are now "much more Vietnamese"
  via the localized labels, and **historical analyses may remain partly English**.
- No payment rollout, credit-gating live, fake data, or admin mutations.

## Retest required after deploy

Redeploy latest `main` (backend + frontend), keep flags false, then:
1. Run a fresh CV analysis (so a succeeded analysis exists).
2. Open `/learning` → confirm the **"Tạo lộ trình học tập từ phân tích gần nhất"**
   CTA (not "analyze again"); click it → Vietnamese tasks appear.
3. Open the analysis result → confirm score-breakdown labels/explanations and the
   limitations are Vietnamese.
4. Resume manual QA Sections 4–8 (Help, Interview, Cover letter, Package, Flags).
