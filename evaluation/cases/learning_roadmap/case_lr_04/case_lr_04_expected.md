# Expected Behavior — Learning Roadmap Case 04: All Skills Listed But Evidence Vague

## CV Profile
CV lists all required skills (FastAPI, PostgreSQL, Redis, Docker) in the skills section. BUT the project descriptions are extremely vague ("Built something", "Used some tools"). No real evidence of actual implementation.

## JD Profile
Standard backend JD with FastAPI, PostgreSQL, Redis, Docker as requirements.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Observed System Behavior
The system treats skills listed in the skills section as "matched skills" (via ontology detection), even when project evidence is vague. As a result, when all skills are listed in the skills section, `build_learning_roadmap` returns an empty list (no missing skills → no roadmap).

### Must include
- Roadmap items are generated based on `missing_skills` list from the scoring result
- Since the system detects skills from the skills section, it may produce 0 roadmap items

### Must NOT include
- Statements saying "since you already have FastAPI/PostgreSQL/Redis/Docker"
- `do_not_claim_until_completed: false` for any skill

## Guardrail Checks
- If roadmap is empty, the system is correctly identifying that no skills are "missing"
- The system must NOT say "you already know X" in the `why` field
