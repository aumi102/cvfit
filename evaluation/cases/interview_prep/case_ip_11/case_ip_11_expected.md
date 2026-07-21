# Expected Behavior — Interview Prep Case 11: Extremely Low Evidence Against Senior JD

## CV Profile
Extremely minimal CV. Only Python and "Simple API" mentioned. No FastAPI, no PostgreSQL, no Redis, no Docker, no cloud, no CI/CD. Massive gap against a senior JD.

## JD Profile
Senior backend engineer JD — most demanding requirements. FastAPI, PostgreSQL, Redis, Docker, Kubernetes, AWS, CI/CD all required.

## Expected Interview Prep Output
The `interview_prep` output must:

### Must include
- Multiple `gap_probe` questions about the many missing skills
- At least 1 `gap_probe` for FastAPI, PostgreSQL, Redis, Docker (all missing)
- `risk_if_user_cannot_answer` must reflect the HIGH RISK of missing most senior requirements
- Answer outlines must include honest learning paths, NOT fabricated senior experience

### Must NOT include
- `project_deep_dive` questions (no relevant evidence exists)
- Questions that pretend "Simple API" is equivalent to FastAPI production experience
- Questions that fabricate Kubernetes, AWS, CI/CD experience

## Guardrail Checks
- No `project_deep_dive` questions (no evidence for any senior requirement)
- Answer outlines must be honest learning paths, NOT fabricated experience
- Questions must NOT claim the candidate has skills they do not have
