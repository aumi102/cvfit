# Expected Behavior — Learning Roadmap Case 08: Multiple Nice-to-Have Skills Missing

## CV Profile
Matches all must-have requirements (FastAPI, PostgreSQL). Missing multiple nice-to-have skills: Redis, Docker, AWS, Kubernetes, GraphQL.

## JD Profile
Backend engineer JD. Must-have: Python, FastAPI, PostgreSQL. Nice-to-have: Redis, Docker, AWS, Kubernetes, GraphQL.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Must include
- Roadmap items for the missing nice-to-have skills
- `priority`: MUST be "medium" or "low" (these are nice-to-have, not blockers)
- `why`: must explain these are nice-to-have per JD
- `do_not_claim_until_completed`: MUST be `true`
- Mini projects should be appropriate for the skill level

### Must NOT include
- Roadmap items for must-have skills (already matched)
- Priority higher than "medium" for nice-to-have skills
- Statements claiming Kubernetes/AWS/GraphQL are requirements

## Guardrail Checks
- All nice-to-have roadmap items must have "medium" or "low" priority
- `do_not_claim_until_completed` MUST be `true`
- Roadmap must NOT overstate the urgency of nice-to-have skills
