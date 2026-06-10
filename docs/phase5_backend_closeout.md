# Phase 5 Backend Closeout

## Status

Phase 5 backend scope owned by Phúc is implementation-complete and unit-test-passed.
Deployed smoke run is pending; this document will be updated with smoke evidence
after the first successful deployed run.

This note contains sanitized handoff evidence only. It does not include access
tokens, database URLs, storage paths, S3 keys, or other secrets.

---

## Completed Backend Scope

All seven Phase 5 backend pillars are implemented:

**Pillar 1 — Application Workspace v1**
- `Application` model with status enum and `best_analysis_job_id` FK.
- CRUD endpoints: `POST`, `GET` (list + single), `PATCH`, `DELETE`.
- Attach-analysis endpoint (`POST .../attach-analysis/{job_id}`) with
  ownership check — `best_analysis_job_id` only settable here, not via PATCH.
- Non-leak ownership convention: cross-user access returns 404.

**Pillar 2 — Application Package v1**
- `ApplicationArtifact` model storing structured payload as JSONB.
- `POST .../package/generate` — builds package from application, attached job,
  and career profile items; stores as artifact.
- `GET .../package` — retrieve latest artifact.
- `GET .../package/download` — JSON download attachment.
- `storage_key` column exists but is never exposed in any response.

**Pillar 3 — Cover Letter Draft v1**
- Evidence-grounded draft generation from analysis result and career profile.
- `POST .../cover-letter/generate`, `GET .../cover-letter`,
  `PATCH .../cover-letter`.
- Disclaimer always preserved — cannot be removed or overwritten by PATCH.
- No fabricated employer names, project names, dates, or metrics.

**Pillar 4 — Interview Practice v2**
- `InterviewAnswer` model with `rubric_json` and `feedback_json` JSONB columns.
- `GET .../interview/questions` — generates up to 8 questions from JD,
  CV evidence, analysis result, and existing `interview_prep` from Result
  JSON v3; falls back to generic behavioral questions when no analysis attached.
- `POST .../interview/answers` — accepts typed answer; scores with deterministic
  rule-based rubric (no LLM scoring call); returns rubric + feedback immediately.
- `GET .../interview/answers` — list all submitted answers per application.
- `risk_gap` is inverse: 0 = no risk, 5 = high risk (per contract Section D).

**Pillar 5 — Career Profile / Evidence Vault v1**
- `CareerProfileItem` model with 7 item types.
- Full CRUD: `POST`, `GET` (list with `?item_type=` filter + single),
  `PATCH`, `DELETE`.
- Profile items are used as evidence context for package, cover letter, and
  interview question generation.

**Pillar 6 — Readiness Summary v1**
- `GET .../readiness` — derives readiness level and next actions from attached
  analysis result.
- Levels: `not_started`, `needs_work`, `almost_ready`, `ready`.
- Disclaimer always included. No hiring guarantees.

**Pillar 7 — Smoke / Release Hardening**
- Phase 5 smoke script: `scripts/smoke_phase5_backend.py`.
- Phase 5 API summary: `docs/phase5_backend_api_summary.md`.
- This closeout document.

---

## Merged PRs

All Phase 5 backend work was delivered through these pull requests merged into `main`:

| PR | Title | Scope |
|---|---|---|
| [#46](https://github.com/somene112/cvfit/pull/46) | docs(phase5): Phase 5 PR1 — contracts and guardrails only | Contracts, guardrails, team plan |
| [#47](https://github.com/somene112/cvfit/pull/47) | feat(phase5): Application Workspace and Career Profile APIs | Pillars 1 + 5: application CRUD, career profile CRUD, readiness summary |
| [#48](https://github.com/somene112/cvfit/pull/48) | feat(phase5): Application Package and Cover Letter APIs | Pillars 2 + 3: package generation, cover letter generation/patch |
| [#49](https://github.com/somene112/cvfit/pull/49) | feat(phase5): Interview Practice APIs | Pillar 4: interview questions, answer submit, rubric scoring |
| [#50](https://github.com/somene112/cvfit/pull/50) | docs(phase5): Backend Integration Smoke + Backend Closeout Draft | Pillar 7: smoke script, API summary, this closeout doc |

---

## Database Migrations

Three Alembic migrations applied in sequence:

| Revision | Description |
|---|---|
| `20260610_0001` | Add `applications` and `career_profile_items` tables |
| `20260610_0002` | Add `application_artifacts` table |
| `20260610_0003` | Add `interview_answers` table |

Expected head after Phase 5: `20260610_0003`.

Run migrations on Render using `scripts/run_alembic.py` as documented in
`docs/render_deployment.md`. Verify `EXPECTED_ALEMBIC_HEAD` in
`backend/app/db/init_db.py` matches after each deploy.

---

## Smoke Evidence

> To be filled in after the first deployed smoke run.

```text
(placeholder — update after deployed run)

API base URL: https://cvfit.onrender.com
phase5 backend smoke passed
```

Sanitized smoke observations to record after run:
- Read-only smoke: health ok, empty list responses ok, no internal fields leaked.
- Mutating smoke: application created, profile item created, interview answer
  submitted, rubric shape verified, cleanup ok.
- With PHASE5_SMOKE_JOB_ID: attach-analysis ok, readiness level returned,
  package generated, cover-letter generated and patched with disclaimer
  preserved, analysis-backed questions returned.

---

## Operational Commands

Read-only Phase 5 smoke (local):

```bat
python scripts\smoke_phase5_backend.py
```

Mutating Phase 5 smoke (local):

```bat
set PHASE5_SMOKE_ALLOW_MUTATING=1
python scripts\smoke_phase5_backend.py
```

Mutating smoke with analysis attachment (deployed):

```bat
set API_BASE_URL=https://cvfit.onrender.com
set PHASE5_SMOKE_ALLOW_MUTATING=1
set PHASE5_SMOKE_JOB_ID=<uuid-of-succeeded-analysis-job>
python scripts\smoke_phase5_backend.py
```

Dry-run (validate config, print expected steps, no API calls):

```bat
python scripts\smoke_phase5_backend.py --dry-run
```

Operational notes:

- `PHASE5_SMOKE_JOB_ID` must be the UUID of an analysis job that (a) belongs
  to the smoke user's account and (b) has `status=succeeded`. Since the smoke
  script creates a fresh synthetic user, the job cannot be pre-owned; this
  parameter is intended for integration environments where a known job UUID
  can be injected by the operator.
- Set `PHASE5_SMOKE_CLEANUP=0` to retain smoke-created resources for manual
  inspection (e.g., to inspect artifact payload_json).
- Mutating smoke creates a synthetic application and career profile item in
  the target environment. By default these are deleted at the end of the run.
- Do not paste access tokens, token-bearing URLs, `DATABASE_URL`, storage
  paths, S3 keys, or screenshots containing secrets into docs, issues, PRs,
  or chat.
- Rotate/reset the database password if `DATABASE_URL` was exposed.
- Run migrations before deploy when a PR includes Alembic migrations.

---

## API Handoff For Quân

Frontend can build against all Phase 5 endpoints. Full endpoint reference is
in `docs/phase5_backend_api_summary.md`.

Key integration points:

- **Applications CRUD** — standard REST under `/v1/applications`.
  Status transitions: frontend should PATCH `status` explicitly after each
  meaningful user action (e.g., after attaching analysis → `analyzing`, after
  generating package → `ready_to_apply`). The backend does not auto-transition
  status.
- **Attach analysis** — use `POST .../attach-analysis/{job_id}`. This is the
  only way to set `best_analysis_job_id`. PATCH does not accept it.
- **Readiness** — render `readiness_level` and `next_actions` as guidance.
  Always show the `disclaimer` field to users. Do not remove or hide it.
- **Package download** — `GET .../package/download` returns JSON with
  `Content-Disposition: attachment`. Current format is `download_format: "json"`.
  PDF/DOCX export is Phase 6 scope.
- **Cover letter** — `payload_json` has a `disclaimer` field. Always render it
  prominently alongside the draft content. Do not allow users to overwrite or
  hide the disclaimer via the PATCH flow.
- **Interview questions** — `GET .../interview/questions` always returns `200`
  (even with no analysis attached). Show the `disclaimer` field to users.
- **Interview answers** — rubric `risk_gap` is inverse: lower is better.
  Consider showing a note like "Gap risk: low / medium / high" rather than
  a raw score. The `feedback.disclaimer` must always be shown to users.
- **Error handling** — `404` means either the resource does not exist or
  belongs to another user. Do not expose this distinction to the UI. `422`
  means invalid input — show the `detail` field.

Frontend reminders:

- Do not log JWT tokens or token-bearing URLs.
- Treat all generated content (cover letter, interview feedback, package) as
  drafts. Always show the disclaimer.
- Do not let users copy-paste `sample_outline` directly into applications —
  it is a scaffold, not a finished product.
- Profile items can be shown as evidence chips in the application workspace.
  `skills_json` for `skill` type items is a list of strings.

---

## Evaluation And QA Handoff For Đạt

Phase 5 evaluation contracts:

- Application workspace: `docs/application_workspace_contract.md`
- Interview practice: `docs/interview_practice_contract.md`

Recommended Phase 5 QA / evaluation focus:

**Guardrail invariants (must pass for every generated output):**
- No fabricated skill names, employer names, project names, metrics, dates,
  certifications, or work experience.
- `missing_evidence` uses "not found in parsed CV" phrasing — never claims
  the user lacks a skill outright.
- `disclaimer` present, non-empty, and unmodified in: readiness response,
  questions response, interview answer feedback, cover letter payload_json,
  application package payload_json.
- `storage_key`, `storage_path`, `password_hash`, `access_token_hash`,
  `report_docx_path` must never appear in any API response.

**Auth and ownership invariants:**
- All endpoints return `401` for missing or invalid JWT.
- Cross-user resource access returns `404` (not `403`).
- `best_analysis_job_id` cannot be set via `PATCH /v1/applications/{id}`.

**Interview practice rubric invariants:**
- Weak answer (short, vague, off-topic): `risk_gap >= 3`,
  non-empty `missing_evidence`, non-empty `suggested_improvements`.
- Strong answer (specific, evidence-grounded, structured): non-empty
  `strengths`, at least one `suggested_improvements` entry.
- All rubric dimensions (`relevance`, `specificity`, `evidence`, `structure`,
  `risk_gap`, `overall`) present and integer 0–5.
- `risk_gap` is inverse: a well-answered gap question should give `risk_gap <= 2`.

**Readiness invariants:**
- `readiness_level` is one of `not_started`, `needs_work`, `almost_ready`, `ready`.
- With no analysis attached: `readiness_level = not_started`, `fit_score = null`.
- With succeeded analysis: `fit_score` matches `overall_fit_score` in result_json.

**Question generation invariants:**
- With no analysis: returns generic `behavioral` type questions, not empty list.
- `gap_probe` questions must state the skill was not found in parsed CV.
- `project_deep_dive` questions must only appear when project evidence exists.
- Maximum 8 questions per call.

---

## Known Follow-Ups

- Deployed smoke run — update smoke evidence section above after first run.
- Frontend UI for all Phase 5 pillars (Quân scope).
- PDF/DOCX export for application package and cover letter (Phase 6).
- LLM-assisted rubric scoring for interview answers (Phase 6).
- Readiness dashboard aggregate view across all applications (Phase 6).
- Cleanup endpoint or smoke artifact cleanup strategy for deployed environments.
- Consider rate-limiting `POST .../interview/answers` per user to prevent
  bulk scoring runs.
