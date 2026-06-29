# Expected Behavior — Interview Prep Case 06: Skills Listed But No Evidence — Questions Must Not Over-Claim

## CV Profile
CV has backend-relevant skills (FastAPI, PostgreSQL, Redis, Docker) AND unrelated skills (Blockchain, Web3, ML, AI, Crypto). The irrelevant skills have NO project evidence.

## JD Profile
Backend engineer JD. Relevant skills are Python, FastAPI, PostgreSQL, Redis, Docker.

## Expected Interview Prep Output
The `interview_prep` output must:

### Must include
- `project_deep_dive` questions about FastAPI/PostgreSQL/Redis/Docker (all are in CV and JD)
- All JD requirements are matched by the system (ontology detects keywords in skills section)

### Must NOT include
- Questions about Blockchain, Web3, ML, AI, Crypto (skills not in JD AND likely lack evidence)
- Questions that pretend unrelated skills are relevant
- Questions that fabricate evidence for skills that are just listed

## Guardrail Checks
- Questions about Blockchain/Web3/ML/AI/Crypto must NOT appear (not in JD, not relevant)
- `project_deep_dive` must only use skills that are in BOTH CV and JD
- Answer outlines must NOT claim expertise in skills without evidence
