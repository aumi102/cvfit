# Expected Behavior — Learning Roadmap Case 12: Must NOT Overstate Nice-to-Have as Requirements

## CV Profile
Matches all must-have requirements (FastAPI, PostgreSQL). Missing Redis, Docker, AWS — all nice-to-have.

## JD Profile
Backend engineer JD. Must-have: Python, FastAPI, PostgreSQL. Nice-to-have: Redis, Docker, AWS.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Must include
- Roadmap items for nice-to-have skills (Redis, Docker, AWS)
- `priority`: "medium" or "low" (nice-to-have, not blockers)
- `why`: must explain these are nice-to-have, helpful but not required

### Must NOT include
- Roadmap items with "high" priority for Redis/Docker/AWS
- Statements that Redis/Docker/AWS are requirements for this role
- Claims that missing these makes the candidate uncompetitive

## Critical Guardrail
Nice-to-have skills must NOT be treated as must-have requirements in the roadmap.

## Guardrail Checks
- Priority must NOT be "high" for nice-to-have skills
- `do_not_claim_until_completed` MUST be `true`
- `why` must NOT overstate the importance of missing nice-to-have skills
