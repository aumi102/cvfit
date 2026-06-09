# Expected Behavior — Interview Prep Case 12: Perfect Match — Standard Questions Expected

## CV Profile
Nearly perfect match. All required skills (Python, FastAPI, PostgreSQL, Redis, Docker) present with project evidence. Also has pytest. This is the ideal candidate for the JD.

## JD Profile
Standard backend JD with exactly the same skills as the CV.

## Expected Interview Prep Output
The `interview_prep` output must:

### Must include
- `project_deep_dive` questions about FastAPI, PostgreSQL, Redis, Docker (all matched in CV)
- **no gap_probe** questions expected — all required skills are matched

### Must NOT include
- Questions about irrelevant skills not in JD
- Questions that fabricate requirements
- Overly basic questions for a matched profile

## Guardrail Checks
- Questions must reference the "API Service" project evidence
- Answer outlines must NOT invent requirements
- No questions about irrelevant skills
