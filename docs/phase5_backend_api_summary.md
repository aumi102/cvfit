# Phase 5 Backend API Summary

**Version:** 1.0
**Date:** 2026-06-10
**Owner (backend):** Phúc
**Audience:** Quân (frontend), Đạt (QA/evaluation)

All Phase 5 endpoints require `Authorization: Bearer <jwt_token>`.
Get a token via `POST /v1/auth/login`. All responses are JSON.
Cross-user resource access returns `404` (not `403`) — non-leak convention.

---

## Auth

| Method | Path | Auth | Status | Description |
|---|---|---|---|---|
| `POST` | `/v1/auth/register` | None | `201` | Register new user |
| `POST` | `/v1/auth/login` | None | `200` | Login; returns `access_token` |

---

## Career Profile / Evidence Vault

Base path: `/v1/profile/items`

| Method | Path | Auth | Status | Description |
|---|---|---|---|---|
| `POST` | `/v1/profile/items` | JWT | `201` | Create a profile item |
| `GET` | `/v1/profile/items` | JWT | `200` | List all profile items (filter: `?item_type=`) |
| `GET` | `/v1/profile/items/{item_id}` | JWT | `200` | Get a single item |
| `PATCH` | `/v1/profile/items/{item_id}` | JWT | `200` | Partial update |
| `DELETE` | `/v1/profile/items/{item_id}` | JWT | `204` | Delete |

**Item types:** `skill`, `project`, `experience`, `education`, `certification`, `achievement`, `link`

**Create / patch body fields:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `item_type` | string | Yes (create) | One of the types above |
| `title` | string | Yes (create) | 1–255 chars |
| `description` | string | No | |
| `skills_json` | array | No | List of skill strings (for `skill` items) |
| `evidence_text` | string | No | Verifiable supporting evidence |
| `source` | string | No | e.g., `"GitHub"`, `"certificate link"` |

---

## Applications

Base path: `/v1/applications`

### CRUD

| Method | Path | Auth | Status | Description |
|---|---|---|---|---|
| `POST` | `/v1/applications` | JWT | `201` | Create application |
| `GET` | `/v1/applications` | JWT | `200` | List owned applications (newest first) |
| `GET` | `/v1/applications/{application_id}` | JWT | `200` | Get single application |
| `PATCH` | `/v1/applications/{application_id}` | JWT | `200` | Partial update (title, company, jd_text, status) |
| `DELETE` | `/v1/applications/{application_id}` | JWT | `204` | Delete |

**Create body fields:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `job_title` | string | Yes | 1–255 chars |
| `company_name` | string | No | |
| `jd_text` | string | Yes | Full JD text |
| `target_role` | string | No | Optional freeform label |

**Application statuses:** `draft` · `analyzing` · `improving_cv` · `ready_to_apply` · `interview_prep` · `applied` · `archived`

> `best_analysis_job_id` is **not** patchable via `PATCH`. Use the attach-analysis endpoint.

---

### Attach Analysis

| Method | Path | Auth | Status | Description |
|---|---|---|---|---|
| `POST` | `/v1/applications/{application_id}/attach-analysis/{job_id}` | JWT | `200` | Attach an owned analysis job to an application |

The `job_id` must be owned by the authenticated user. Returns `{ application_id, best_analysis_job_id }`.

---

### Readiness Summary

| Method | Path | Auth | Status | Description |
|---|---|---|---|---|
| `GET` | `/v1/applications/{application_id}/readiness` | JWT | `200` | Readiness summary derived from attached analysis |

**Readiness levels:** `not_started` · `needs_work` · `almost_ready` · `ready`

Returns `fit_score` (float or null), `readiness_level`, `summary`, and `next_actions` list.

---

### Application Package

| Method | Path | Auth | Status | Description |
|---|---|---|---|---|
| `POST` | `/v1/applications/{application_id}/package/generate` | JWT | `201` | Generate application package artifact |
| `GET` | `/v1/applications/{application_id}/package` | JWT | `200` | Retrieve latest package artifact |
| `GET` | `/v1/applications/{application_id}/package/download` | JWT | `200` | Download package as JSON attachment |

Requires `best_analysis_job_id` to be set before generating (returns `422` otherwise).
`storage_key` is not exposed in any response.

---

### Cover Letter Draft

| Method | Path | Auth | Status | Description |
|---|---|---|---|---|
| `POST` | `/v1/applications/{application_id}/cover-letter/generate` | JWT | `201` | Generate cover letter draft artifact |
| `GET` | `/v1/applications/{application_id}/cover-letter` | JWT | `200` | Retrieve latest cover letter draft |
| `PATCH` | `/v1/applications/{application_id}/cover-letter` | JWT | `200` | Patch sections of the cover letter |

Requires `best_analysis_job_id` to be set before generating (returns `422` otherwise).

**Patchable fields:** `opening`, `why_role_company`, `relevant_evidence`, `contribution_fit`, `closing`, `review_notes`

> `disclaimer` is always preserved — it cannot be removed or overwritten by `PATCH`.

---

### Interview Practice

| Method | Path | Auth | Status | Description |
|---|---|---|---|---|
| `GET` | `/v1/applications/{application_id}/interview/questions` | JWT | `200` | Generate practice questions |
| `POST` | `/v1/applications/{application_id}/interview/answers` | JWT | `201` | Submit a typed answer; returns rubric + feedback |
| `GET` | `/v1/applications/{application_id}/interview/answers` | JWT | `200` | List all submitted answers |

**GET questions behavior:**
- If no analysis job is attached: returns generic behavioral questions (always `200`).
- If analysis job is attached: returns evidence-grounded questions (technical, behavioral, project deep-dive, gap probe).
- Always includes `disclaimer` in response.

**POST answers request body:**

| Field | Type | Constraints |
|---|---|---|
| `question_id` | string | 1–100 chars |
| `question` | string | 1–1000 chars |
| `answer_text` | string | 1–8000 chars |

**Rubric schema:**

| Dimension | Scale | Notes |
|---|---|---|
| `relevance` | 0–5 | Does the answer address the question? |
| `specificity` | 0–5 | Specific details, tools, outcomes |
| `evidence` | 0–5 | References verifiable CV/profile evidence |
| `structure` | 0–5 | STAR or similar structure |
| `risk_gap` | 0–5 | **Inverse: 0=no risk, 5=high risk** |
| `overall` | 0–5 | Holistic score |

Scoring is deterministic (rule-based); no LLM scoring call in Phase 5.

**Feedback fields:** `strengths`, `missing_evidence`, `suggested_improvements`, `sample_outline`, `risk_notes`, `disclaimer`

---

## Error Codes (All Phase 5 Endpoints)

| Code | Meaning |
|---|---|
| `401` | JWT missing or invalid |
| `404` | Resource not found, or belongs to another user (non-leak) |
| `422` | Missing required fields, invalid values, or precondition not met |

---

## Security Notes for Quân

- Never log JWT tokens or token-bearing URLs.
- Do not display `jd_text` in collapsed form if it would expose candidate PII.
- Treat `readiness_level` and `fit_score` as preparation signals, not guarantees — the backend includes a `disclaimer` field in readiness and feedback responses; render it to users.
- `sample_outline` in interview feedback uses the user's own evidence. Do not let users copy and submit it as-is without review — the disclaimer covers this.
- All artifact `payload_json` is structured JSON; parse and render field-by-field. Do not eval or inject it directly into HTML.

## QA Notes for Đạt

- Phase 5 backend evaluation targets are documented in `docs/interview_practice_contract.md` (Section I) and `docs/application_workspace_contract.md`.
- Key invariants to verify:
  - No fabricated skill names, employer names, project names, or metrics in any generated content.
  - `missing_evidence` uses "not found in parsed CV" semantics — never claims user lacks a skill.
  - `disclaimer` present and non-empty in: readiness response, questions response, feedback response, cover letter `payload_json`, package `payload_json`.
  - `storage_key`, `storage_path`, `password_hash`, `access_token_hash`, `report_docx_path` never appear in any response.
  - Cross-user resource access returns `404`, not `403`.
  - `best_analysis_job_id` cannot be set via `PATCH /v1/applications/{id}`.
  - Weak answer → `risk_gap >= 3`, non-empty `missing_evidence`, non-empty `suggested_improvements`.
  - Strong answer → non-empty `strengths`, at least one `suggested_improvements` entry.
