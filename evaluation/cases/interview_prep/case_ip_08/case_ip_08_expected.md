# Expected Behavior — Interview Prep Case 08: Missing Most Required Skills

## CV Profile
Very weak profile. Python and Flask (acceptable) but no FastAPI, no PostgreSQL, no Docker, no tests. "Learning Projects" is extremely vague.

## JD Profile
Junior backend developer requiring Python, Flask (or FastAPI), PostgreSQL basics, Docker basics.

## Expected Interview Prep Output
The `interview_prep` output must:

### Must include
- `gap_probe` questions about FastAPI (Flask ≠ FastAPI for junior role), PostgreSQL, Docker
- Questions must honestly acknowledge that evidence was not found
- Answer outlines must NOT fabricate experience. MUST include honest learning paths
- `risk_if_user_cannot_answer` should reflect that missing most requirements is a high risk for this role

### Must NOT include
- `project_deep_dive` about FastAPI (no FastAPI evidence in CV)
- `project_deep_dive` about PostgreSQL (no PostgreSQL evidence)
- Questions that pretend the learning projects are equivalent to production experience

## Guardrail Checks
- No `project_deep_dive` questions about missing skills (only gap_probe)
- Answer outlines must include honest learning guidance, NOT fabricated production experience
- Questions must reflect the high risk of missing most requirements
