# Expected Behavior — Interview Prep Case 13: Good Match With Auth and Background Tasks

## CV Profile
Good match for the JD with some bonus skills. FastAPI, PostgreSQL, Redis, Docker all present. Also has Celery (background tasks) and JWT (auth) — matching the JD's extra requirements. Evidence is somewhat brief but present.

## JD Profile
Backend engineer with standard requirements plus background tasks and authentication.

## Expected Interview Prep Output
The `interview_prep` output must:

### Must include
- `project_deep_dive` questions about FastAPI/PostgreSQL/Redis/Docker (core skills)
- At least 1 `project_deep_dive` question about Celery (background tasks — bonus skill in CV)
- At least 1 `project_deep_dive` question about JWT authentication
- `risk_if_user_cannot_answer` for each should reflect the evidence quality

### Must NOT include
- Questions about skills not in JD (e.g., Kubernetes, AWS, GraphQL)
- Questions that fabricate architectural details

## Guardrail Checks
- Questions must reference specific evidence from the "Production API" project
- Answer outlines must NOT invent implementation details
- No questions about irrelevant skills
