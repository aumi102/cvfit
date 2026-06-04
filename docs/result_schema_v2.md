# Result JSON v2 Contract

## Purpose

Result JSON v2 is the shared backend-to-frontend contract for a completed CV fit analysis. It should make the scoring result understandable, auditable, and report-ready without requiring the frontend, history page, report generator, or evaluation scripts to reverse-engineer scorer internals.

The contract is intentionally a product/API contract first. Phase 3.1 does not implement the new payload. Later backend work should adapt the current scorer output into this shape while preserving Phase 2 auth, history, result, and report download behavior.

## Backward Compatibility Rule

The existing completed-job flow must keep working:

- `GET /v1/jobs/{job_id}/result` must continue to return the current response envelope with `job_id`, nested `result`, and safe top-level convenience fields.
- `result.fit_score` must remain available if any frontend, smoke script, or report code depends on it during the transition.
- `result.scores.fit_score` must remain available while current static frontend and smoke scripts depend on it.
- `result.overall.fit_score` should also exist in v2.
- The API-level convenience field `overall_fit_score` should remain available for history/result compatibility.
- Existing auth/history/report download flow must not break. Owner JWT access and guest `access_token` access must keep the same authorization behavior.
- Internal fields such as `storage_path`, `report_docx_path`, `access_token`, `access_token_hash`, local paths, S3 object keys, or raw CV text must not be exposed.

Recommended transition shape:

```json
{
  "job_id": "3b8d9a2a-13b8-4c7e-9b53-8a2a6f6f1b4e",
  "overall_fit_score": 78.4,
  "summary": "Good fit with clear Python and FastAPI evidence, but weaker Kubernetes and observability evidence.",
  "strengths": [],
  "missing_skills": [],
  "recommendations": [],
  "evidence": [],
  "result": {
    "schema_version": "2.0",
    "fit_score": 78.4,
    "scores": {
      "fit_score": 78.4,
      "skill_match": 82.0,
      "responsibility_match": 76.3,
      "experience_level": 70.0,
      "project_relevance": 81.2,
      "cv_quality": 87.5
    },
    "overall": {
      "fit_score": 78.4,
      "fit_level": "good",
      "summary": "Good fit with clear Python and FastAPI evidence, but weaker Kubernetes and observability evidence.",
      "confidence": 0.82,
      "guardrail_notice": "This analysis estimates CV-to-JD fit only and does not guarantee any hiring outcome."
    }
  }
}
```

## Proposed Result Object

The object below is the proposed `result` value stored in `analysis_jobs.result_json` and returned under the API response's nested `result` key.

```json
{
  "schema_version": "2.0",
  "job_id": "3b8d9a2a-13b8-4c7e-9b53-8a2a6f6f1b4e",
  "fit_score": 78.4,
  "scores": {
    "fit_score": 78.4,
    "skill_match": 82.0,
    "responsibility_match": 76.3,
    "experience_level": 70.0,
    "project_relevance": 81.2,
    "cv_quality": 87.5
  },
  "overall": {
    "fit_score": 78.4,
    "fit_level": "good",
    "summary": "Good fit with clear Python and FastAPI evidence, but weaker Kubernetes and observability evidence.",
    "confidence": 0.82,
    "guardrail_notice": "This analysis estimates CV-to-JD fit only and does not guarantee any hiring outcome."
  },
  "score_breakdown": [
    {
      "key": "skill_match",
      "label": "Skill match",
      "score": 82.0,
      "weight": 0.35,
      "explanation": "Most required backend skills were found in the CV."
    },
    {
      "key": "responsibility_match",
      "label": "Responsibility match",
      "score": 76.3,
      "weight": 0.30,
      "explanation": "Several CV bullets are semantically close to the JD responsibilities."
    },
    {
      "key": "experience_level",
      "label": "Experience level",
      "score": 70.0,
      "weight": 0.15,
      "explanation": "The CV shows some relevant timeline evidence, but seniority is not strongly proven."
    },
    {
      "key": "project_relevance",
      "label": "Project relevance",
      "score": 81.2,
      "weight": 0.10,
      "explanation": "Project bullets are relevant to API and backend delivery."
    },
    {
      "key": "cv_quality",
      "label": "CV quality",
      "score": 87.5,
      "weight": 0.10,
      "explanation": "The CV is parseable and has useful structure, but could include more measurable impact."
    }
  ],
  "matched_skills": [
    {
      "skill": "FastAPI",
      "requirement_type": "must_have",
      "jd_requirement": "Experience with Python and FastAPI",
      "match_type": "direct",
      "confidence": 0.95,
      "cv_evidence_ids": ["ev_cv_001"],
      "jd_evidence_ids": ["ev_jd_001"],
      "notes": "Direct skill mention found in CV text."
    },
    {
      "skill": "PostgreSQL",
      "requirement_type": "must_have",
      "jd_requirement": "PostgreSQL or MySQL",
      "match_type": "alias_or_group",
      "confidence": 0.9,
      "cv_evidence_ids": ["ev_cv_002"],
      "jd_evidence_ids": ["ev_jd_002"],
      "notes": "Matched one acceptable option from the JD skill group."
    }
  ],
  "missing_skills": [
    {
      "skill": "Kubernetes",
      "requirement_type": "nice_to_have",
      "jd_requirement": "Docker and Kubernetes experience is a plus",
      "severity": "medium",
      "reason": "No CV evidence was found for Kubernetes.",
      "jd_evidence_ids": ["ev_jd_003"],
      "suggestion": "If you have actually used Kubernetes, add a truthful CV bullet with project context, tools used, and measurable outcome. Only add this if it is true."
    }
  ],
  "evidence": [
    {
      "id": "ev_cv_001",
      "source": "cv",
      "kind": "skill",
      "text": "Built backend APIs with Python, FastAPI, PostgreSQL, Redis, and Docker.",
      "normalized_skill": "FastAPI",
      "location": {
        "section": "experience",
        "page": null,
        "line": null
      },
      "confidence": 0.95
    },
    {
      "id": "ev_jd_001",
      "source": "jd",
      "kind": "requirement",
      "text": "Experience with Python and FastAPI.",
      "normalized_skill": "FastAPI",
      "location": {
        "section": "requirements",
        "line": null
      },
      "confidence": 0.9
    },
    {
      "id": "ev_cv_010",
      "source": "cv",
      "kind": "responsibility",
      "text": "Implemented background workers and deployment checks for API services.",
      "best_cv_bullet": "Implemented background workers and deployment checks for API services.",
      "jd_requirement": "Troubleshoot background workers and deployment issues.",
      "jd_evidence_ids": ["ev_jd_resp_001"],
      "similarity": 0.8123,
      "confidence": 0.81
    }
  ],
  "improvement_actions": [
    {
      "id": "act_001",
      "type": "cv_rewrite",
      "priority": "high",
      "title": "Add conditional FastAPI project evidence",
      "suggestion": "If you have actually used FastAPI, add a project bullet describing the API endpoint, database, deployment, and measurable outcome.",
      "related_skill": "FastAPI",
      "related_evidence_ids": ["ev_jd_001"],
      "guardrail": "Only add this if it is true."
    },
    {
      "id": "act_002",
      "type": "skill_gap",
      "priority": "medium",
      "title": "Address Kubernetes gap",
      "suggestion": "If you have Kubernetes experience, add the cluster, workload, or deployment responsibility you handled. If not, treat this as a learning gap rather than claiming it.",
      "related_skill": "Kubernetes",
      "related_evidence_ids": ["ev_jd_003"],
      "guardrail": "Do not invent experience."
    }
  ],
  "limitations": [
    "This analysis is based on parsed CV/JD text and may miss information if the document parser failed to extract it.",
    "The score estimates CV-to-JD fit and does not guarantee interview selection, job offer, or hiring outcome.",
    "Missing evidence means the system did not find support in the parsed CV, not that the candidate definitely lacks the skill."
  ],
  "metadata": {
    "generated_at": "2026-06-04T09:30:00Z",
    "scorer_version": "phase3.result_json_v2",
    "language": "en",
    "strictness": "balanced",
    "target_role": "Backend Engineer",
    "cv": {
      "file_name": "candidate_cv.docx",
      "parsed_confidence": 0.85,
      "skills_detected": ["Docker", "FastAPI", "PostgreSQL", "Python", "Redis"]
    },
    "jd": {
      "role": "Backend Engineer",
      "must_have_skill_groups": [["python"], ["fastapi"], ["postgresql", "mysql"]],
      "nice_to_have_skill_groups": [["kubernetes"]],
      "responsibility_count": 8
    }
  }
}
```

## Field Definitions

### `overall`

High-level score summary for the result card, history summaries, report summary, and evaluation comparisons.

- `fit_score`: Number from `0` to `100`. Same value as `result.fit_score`, `result.scores.fit_score`, and API `overall_fit_score`.
- `fit_level`: One of `excellent`, `good`, `partial`, or `weak`.
- `summary`: Short, human-readable summary grounded in matched and missing evidence.
- `confidence`: Optional number from `0` to `1` representing confidence in the analysis quality, not hiring likelihood.
- `guardrail_notice`: Required user-facing warning that the result does not guarantee a hiring outcome.

### `score_breakdown`

Ordered list of scoring components. Use this for UI charts, reports, and evaluation diagnostics.

- `key`: Stable machine key, for example `skill_match`.
- `label`: UI/report label.
- `score`: Component score from `0` to `100`.
- `weight`: Contribution to `overall.fit_score`. Weights should sum to `1.0` when all components are present.
- `explanation`: Short explanation grounded in the component result.

### `matched_skills`

Skills or skill groups from the JD that have support in the parsed CV.

- `skill`: Normalized skill name shown to users.
- `requirement_type`: `must_have`, `nice_to_have`, or `responsibility`.
- `jd_requirement`: Original or summarized JD requirement.
- `match_type`: `direct`, `alias_or_group`, `semantic`, or `inferred_from_project`.
- `confidence`: Number from `0` to `1`.
- `cv_evidence_ids`: Required when CV evidence is found. Points into `evidence`.
- `jd_evidence_ids`: Optional but preferred when JD evidence is available.
- `notes`: Optional short explanation. Must not claim facts beyond evidence.

### `missing_skills`

JD skills or requirements with insufficient CV evidence.

- `skill`: Normalized skill or grouped requirement label.
- `requirement_type`: `must_have`, `nice_to_have`, or `responsibility`.
- `jd_requirement`: Original or summarized JD requirement.
- `severity`: `high`, `medium`, or `low`.
- `reason`: Explain that evidence was not found or was too weak.
- `jd_evidence_ids`: Optional but preferred when the missing requirement maps to specific JD text.
- `suggestion`: Optional conditional next step. Must include truthful-use wording such as `If you have actually used X...` and `Only add this if it is true.`

### `evidence`

Evidence snippets supporting matched skills, responsibility matches, missing JD requirements, and improvement actions.

- `id`: Stable ID unique within the result, for example `ev_cv_001`.
- `source`: `cv` or `jd`.
- `kind`: `skill`, `requirement`, `responsibility`, `quality`, or `parser`.
- `text`: Short snippet from parsed CV or JD text. Do not include hidden storage paths or secrets.
- `normalized_skill`: Optional normalized skill for skill evidence.
- `jd_requirement`: Optional matched JD responsibility/requirement for responsibility evidence.
- `best_cv_bullet`: Optional CV bullet for responsibility evidence when available.
- `jd_evidence_ids`: Optional JD evidence IDs for responsibility evidence when the matching JD requirement is known.
- `location`: Optional parser location such as section, page, or line. Use `null` when unknown.
- `similarity`: Optional semantic similarity score for responsibility matches.
- `confidence`: Optional number from `0` to `1`.

### `improvement_actions`

Concrete next actions for the candidate. These must be conditional and must not instruct the user to fabricate experience.

- `id`: Stable ID unique within the result.
- `type`: `cv_rewrite`, `skill_gap`, `project_detail`, `metrics`, `formatting`, or `learning`.
- `priority`: `high`, `medium`, or `low`.
- `title`: Short action title.
- `suggestion`: Conditional user-facing suggestion.
- `related_skill`: Optional skill.
- `related_evidence_ids`: Evidence IDs that justify the action.
- `guardrail`: Short reminder such as `Only add this if it is true.`

### `limitations`

Plain-language caveats that explain parser, scoring, and product limitations. Include at least:

- No guaranteed hiring outcome.
- Parsed text may be incomplete.
- Missing evidence does not prove the candidate lacks the skill.

### `metadata`

Non-sensitive operational metadata useful for debugging, reports, and evaluation.

- `generated_at`: ISO-8601 timestamp.
- `scorer_version`: Backend scorer/enricher version.
- `language`: Requested output language.
- `strictness`: Requested strictness.
- `target_role`: Requested or inferred role.
- `cv`: Safe CV metadata only, such as file name, parsed confidence, and detected skills.
- `jd`: Safe JD metadata only, such as inferred role and requirement counts/groups.

## Fit Level Rules

Use the same thresholds everywhere: backend result, frontend display, report, and evaluation.

- `excellent`: `fit_score >= 85`. Strong coverage of must-have skills, relevant responsibilities, and good CV evidence quality.
- `good`: `70 <= fit_score < 85`. Good practical fit with some gaps or weaker evidence.
- `partial`: `50 <= fit_score < 70`. Some relevant overlap, but important requirements are missing or weakly evidenced.
- `weak`: `fit_score < 50`. Limited evidence for key JD requirements.

Fit level should not override the score. If a critical must-have skill is missing, later scoring work may cap the fit level below `excellent` even when the numeric score is high, but that cap should be explicit in `overall.summary` or `limitations`.

## Evidence Rules

- Every matched skill must include CV evidence when found.
- JD requirement evidence should be included when practical, especially for must-have requirements and missing skills.
- Evidence text must come from parsed CV/JD content or deterministic parser/scorer metadata.
- If no evidence is found, say missing evidence. Do not invent evidence.
- Alias/group matches must explain which JD option was satisfied.
- Semantic responsibility matches must include the CV snippet, JD requirement, and similarity/confidence when available.
- Evidence snippets should be short enough for UI/report display and must not expose internal paths, tokens, buckets, object keys, or raw full CV text.

## Guardrail Wording

Required wording concepts for result and report surfaces:

- No guaranteed hiring outcome: "This analysis estimates CV-to-JD fit only and does not guarantee any hiring outcome."
- Do not invent skills.
- Do not invent experience.
- Suggestions must be conditional. Example: "If you have actually used FastAPI, add a project bullet describing it."
- Missing evidence must be phrased as "not found in the parsed CV" or equivalent, not as an absolute claim that the candidate lacks the skill.

## Compatibility Plan

1. Keep storing and returning the current v1-like result until the v2 wrapper is ready.
2. Add a backend wrapper/enricher that takes the existing scorer output and emits v2 fields without removing legacy fields.
3. During transition, return all score aliases:
   - API envelope: `overall_fit_score`
   - Nested result root: `fit_score`
   - Nested legacy scores: `scores.fit_score`
   - Nested v2 summary: `overall.fit_score`
4. Keep `_result_contract_fields` deriving top-level fields from either v1 or v2 shapes.
5. Keep `_scrub_internal_fields` applied to the full result payload.
6. Update DOCX report generation after the API result shape is stable.
7. Update frontend only after backend compatibility tests prove v1 consumers still pass.
8. Add `schema_version` so evaluation scripts can distinguish v1, transitional v2, and final v2 payloads.

## Suggested Implementation Phases

### Phase 3.1 Contract Only

Create this document. No backend behavior change.

### Phase 3.2 Scoring Wrapper/Enricher

Add a result builder that maps current scorer output to Result JSON v2 and preserves legacy aliases. Keep current scoring math unless intentionally changed in a later scoring task.

### Phase 3.3 Evidence Mapping

Improve evidence IDs, CV/JD snippet mapping, missing-evidence wording, and responsibility evidence. Add deterministic tests for no-invention behavior.

### Phase 3.4 Report v2

Update DOCX generation to consume v2 sections: overall, score breakdown, matched skills, missing skills, evidence, improvement actions, limitations, and guardrails.

Report DOCX v2 should read the structured `overall`, `score_breakdown`, `matched_skills`, `missing_skills`, `evidence`, `improvement_actions`, and `limitations` sections when present, while keeping legacy fallbacks for older stored results.

MVP smoke tests should keep requiring legacy `result.scores.fit_score` for backward compatibility. Phase 3 deployments can set `REQUIRE_RESULT_V2=1` for mutating smoke runs to require `schema_version: "2.0"` and the core v2 result fields.

### Phase 3.5 Smoke/Evaluation

Add smoke and evaluation checks that assert compatibility aliases, evidence structure, report availability, auth/history access, and no internal field leakage.

## Backend Implementation Notes

Candidate files/functions to update later based on the audit:

- `backend/app/workers/tasks.py`: `run_job` builds `result_full`, stores `AnalysisJob.result_json`, and calls `build_docx_report`.
- `backend/app/services/scoring/scorer.py`: `score`, `evaluate_skill_groups`, `evaluate_responsibilities`, `evaluate_cv_quality`, and `build_learning_plan` generate the current score, skills, gaps, evidence, and improvement-like data.
- `backend/app/api/routes/jobs.py`: `job_result`, `_result_contract_fields`, `_history_item`, and `_scrub_internal_fields` shape result/history API responses and enforce safe output.
- `backend/app/schemas/responses.py`: `JobResultResponse` and `JobHistoryItemResponse` define the API envelope and top-level compatibility fields.
- `backend/app/services/reporting/report_docx.py`: `build_docx_report` currently reads legacy `scores`, `skill_gap`, `cv_improvements`, and `evidence`.
- `backend/app/db/models.py`: `AnalysisJob.result_json` is the JSONB storage column; no schema migration should be needed for v2 if it remains JSONB.
- Frontend inspection only: `frontend/src/services/jobApi.js`, `frontend/src/app/dashboard/page.js`, `frontend/src/components/dashboard/ResultCard.jsx`, `frontend/src/app/history/page.js`, and `frontend/static/app.js` reveal current result/history/report assumptions.

Risks:

- Current static frontend and `scripts/smoke_test_mvp.py` require `result.result.scores.fit_score`.
- Current history API derives `overall_fit_score` from `result_json.scores.fit_score`.
- The Next dashboard result card appears to look for `overall_score` or `score`, while the API currently returns `overall_fit_score`; updating the API/frontend contract should avoid introducing another score alias mismatch.
- Evidence currently has mixed shapes and no stable IDs, so report/frontend rendering should not depend on v2 evidence IDs until Phase 3.3 is implemented.
- Improvement suggestions must be rewritten with conditional guardrails; current `cv_improvements` and learning suggestions are useful inputs but are not yet guardrail-complete.
- Any result-shape change can break report generation because `report_docx.py` currently reads legacy keys directly.

Tests that should be added later:

- Unit tests for a v2 result builder/enricher preserving `fit_score`, `scores.fit_score`, `overall.fit_score`, and API `overall_fit_score`.
- Unit tests for fit level thresholds: `excellent`, `good`, `partial`, and `weak`.
- API tests for `GET /v1/jobs/{job_id}/result` with guest `access_token`, owner JWT, wrong token, and non-owner JWT.
- API/history tests proving `overall_fit_score`, `has_report`, and `target_role` still work with v2 stored results.
- Scrubbing tests proving v2 evidence/metadata cannot expose storage paths, S3 keys, local paths, access tokens, or raw full CV text.
- Report tests proving DOCX generation works from v2 and still downloads through the existing authorized endpoint.
- Guardrail tests for missing evidence and conditional improvement wording.

Smoke scripts that should be checked later:

- `scripts/smoke_test_mvp.py`: currently asserts `result.result.scores.fit_score` and downloads DOCX.
- `scripts/smoke_test_local.py`: checks result/report/download in local worker flow.
- `scripts/smoke_phase1_backend.py`: checks access-token rejection/acceptance and result/report safety.
- `scripts/smoke_test_auth_api.py`: auth-only smoke should remain unaffected but protects Phase 2 login assumptions.
- `scripts/smoke_test_s3.py`: delegates to local smoke and should still validate S3 report storage/download after report v2.
