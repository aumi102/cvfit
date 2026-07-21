# Expected Behavior — Learning Roadmap Case 07: Only Nice-to-Have Skills Missing

## CV Profile
Partial match. Python and FastAPI present with some evidence. PostgreSQL present. Redis and Docker are missing — but both are "nice to have" not required. AWS is also nice-to-have.

## JD Profile
Backend developer JD. Must-have: Python, FastAPI, PostgreSQL. Nice-to-have: Redis, Docker, AWS.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Must include
- Roadmap items for Redis, Docker, AWS if roadmap items are generated
- `priority`: should be "medium" (nice-to-have, not blockers)
- `why`: must explain these are nice-to-have, not critical requirements
- `do_not_claim_until_completed`: MUST be `true`

### Must NOT include
- Roadmap items for Python, FastAPI, PostgreSQL (already matched)
- Roadmap items with "high" priority (nice-to-have skills should not be "high" priority)
- Statements implying Redis/Docker/AWS are required

## Guardrail Checks
- Priority for nice-to-have skills must NOT be "high"
- Roadmap must NOT overstate the importance of missing nice-to-have skills
- `do_not_claim_until_completed` MUST be `true`
