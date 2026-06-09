# Expected Behavior — Interview Prep Case 09: One Skill Missing — Focus on Gap

## CV Profile
Good backend profile. FastAPI, PostgreSQL, Docker all present with project evidence. Redis is completely missing — this is the only gap.

## JD Profile
Standard backend JD. Redis is explicitly required.

## Expected Interview Prep Output
The `interview_prep` output must:

### Must include
- `project_deep_dive` questions about FastAPI/PostgreSQL/Docker (matched skills with evidence)
- At least 1 `gap_probe` question about Redis (the one missing skill)
- The `gap_probe` about Redis must:
  - Have non-empty `related_jd_requirement`
  - Have empty `related_cv_evidence`
  - Have honest `why_this_question` about the gap
  - Have `suggested_answer_outline` that includes honest learning guidance, NOT fabricated Redis experience

### Must NOT include
- Questions that claim the candidate has Redis experience
- Questions about irrelevant skills not in JD

## Guardrail Checks
- `gap_probe` about Redis must have empty `related_cv_evidence` (Redis not found in CV)
- Answer outlines for gap questions must include learning paths, NOT fabricated claims
- No questions about irrelevant skills
