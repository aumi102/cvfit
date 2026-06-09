# Expected Behavior — Interview Prep Case 05: Junior Profile — Mostly Matched, Minimal Gaps

## CV Profile
Junior developer with FastAPI learning project. Has FastAPI evidence (todo API) but no production database, no Docker. The CV explicitly says "no PostgreSQL" and "no Docker". HOWEVER, the ontology detects these keywords in the text, so the system may match them as "detected skills" even though the CV disclaims them.

## JD Profile
Junior backend developer JD — less demanding than senior JD. Docker is "basics", PostgreSQL is "basic usage".

## Expected Interview Prep Output
The `interview_prep` output must:

### Must include
- `project_deep_dive` questions about FastAPI (matched skill with evidence)
- System may match PostgreSQL/Docker (detected as keywords) even though CV disclaims them
- Answer outlines appropriate for a junior level

### Must NOT include
- Questions asking for production-scale experience
- Questions about senior-level topics (architecture decisions, team leadership)
- Questions about Kubernetes or AWS (not in JD)

## Guardrail Checks
- Questions must be calibrated to junior level
- Answer outlines must NOT invent senior-level experience
- No questions about irrelevant skills
