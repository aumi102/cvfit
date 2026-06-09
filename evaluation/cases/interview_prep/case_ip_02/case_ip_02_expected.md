# Expected Behavior — Interview Prep Case 02: No Relevant Backend Skills

## CV Profile
Frontend-only profile. No Python, no backend framework, no database, no deployment experience. Zero overlap with the backend JD.

## JD Profile
Backend engineer requiring FastAPI, PostgreSQL, Redis, Docker — skills completely absent from CV.

## Expected Interview Prep Output
The `interview_prep` output must:

### Must include
- At least 1 `gap_probe` question about the missing backend skills
- Questions must probe Python, FastAPI, PostgreSQL, Redis, Docker gaps honestly
- The `gap_probe` question must include `risk_if_user_cannot_answer` explaining the gap risk
- The `why_this_question` must acknowledge the skill is missing from CV

### Must NOT include
- Questions that claim the candidate has FastAPI/PostgreSQL/Redis experience
- Questions that pretend the frontend work is backend-relevant
- Questions that dive into backend project evidence (candidate has no backend project evidence)

## Required Fields
- `gap_probe` questions must have non-empty `related_cv_evidence` (empty list allowed — no evidence exists)
- `gap_probe` questions must have non-empty `risk_if_user_cannot_answer`
- Answer outlines must include honest preparation guidance, NOT fabricated experience

## Guardrail Checks
- Backend project deep-dive questions must NOT appear (no backend project evidence in CV)
- Questions must NOT fabricate backend experience from frontend work
- Answer outlines must NOT invent project details
