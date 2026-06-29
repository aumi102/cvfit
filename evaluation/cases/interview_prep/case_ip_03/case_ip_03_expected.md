# Expected Behavior — Interview Prep Case 03: Partial Match — Some Skills Present, Some Missing

## CV Profile
Partial backend match. FastAPI is present but with weak evidence (no project details, no scope). PostgreSQL, Redis, Docker are missing entirely.

## JD Profile
Standard backend JD requiring FastAPI, PostgreSQL, Redis, Docker.

## Expected Interview Prep Output
The `interview_prep` output must contain questions for BOTH matched and missing skills:

### Must include
- At least 1 `project_deep_dive` question about FastAPI (matched skill)
  - BUT must acknowledge evidence is shallow in `why_this_question`
  - `risk_if_user_cannot_answer` should reflect the weak evidence risk
- At least 1 `gap_probe` question about PostgreSQL, Redis, or Docker (missing skills)
  - Must honestly acknowledge missing evidence in `why_this_question`
  - Answer outline must NOT fabricate PostgreSQL/Redis/Docker experience

### Must NOT include
- Questions that claim the candidate has PostgreSQL/Redis/Docker evidence
- Questions about unrelated skills
- `project_deep_dive` about a skill with NO evidence in CV

## Guardrail Checks
- `project_deep_dive` about FastAPI must reference the "Internal API" evidence
- `gap_probe` about PostgreSQL/Redis/Docker must have empty `related_cv_evidence`
- Answer outlines must include honest guidance, not invented details
