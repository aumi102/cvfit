# Expected Behavior — Interview Prep Case 04: Vague Evidence — Questions Should Acknowledge

## CV Profile
CV has all required skills in the skills list (FastAPI, PostgreSQL, Redis, Docker) but the project descriptions are extremely vague ("Built APIs", "Used databases", "Deployed with Docker"). No concrete evidence of actual implementation.

## JD Profile
Standard backend JD requiring FastAPI, PostgreSQL, Redis, Docker.

## Expected Interview Prep Output
The `interview_prep` output must:

### Must include
- At least 1 `project_deep_dive` question about the backend work
- `risk_if_user_cannot_answer` MUST reflect the shallow evidence risk (candidate may not be able to answer due to vague CV)
- `why_this_question` should acknowledge that evidence is thin
- `related_cv_evidence` should reference the vague "Backend Work" project

### Must NOT include
- Questions that assume the candidate has deep FastAPI/PostgreSQL/Redis/Docker experience
- Questions that fabricate specific requirements not in the CV
- Questions about skills not in JD

## Guardrail Checks
- `risk_if_user_cannot_answer` must be meaningful and reflect the evidence gap
- Questions must NOT fabricate implementation details (no specific endpoints, metrics, scale claims)
- Answer outlines must NOT invent project requirements
