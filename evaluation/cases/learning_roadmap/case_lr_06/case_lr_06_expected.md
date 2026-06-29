# Expected Behavior — Learning Roadmap Case 06: Nice-to-Have Skills Missing

## CV Profile
Good backend profile matching all must-have requirements. FastAPI, PostgreSQL, Redis, Docker all present with project evidence. Kubernetes, AWS, GraphQL are missing but they are "nice to have" not required.

## JD Profile
Backend engineer JD. Must-have: FastAPI, PostgreSQL, Redis, Docker. Nice-to-have: Kubernetes, AWS, GraphQL.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Must include
- Roadmap items for nice-to-have skills (Kubernetes, AWS, GraphQL) if any roadmap items are generated
- `priority`: should be "medium" or "low" for nice-to-have skills (not "high")
- `why`: must explain these are nice-to-have per JD, not blockers

### Must NOT include
- Roadmap items for must-have skills that are already matched (FastAPI, PostgreSQL, Redis, Docker)
- Roadmap items with "high" priority for nice-to-have skills
- Statements claiming the user needs these to be competitive

## Guardrail Checks
- Nice-to-have skills should have lower priority than must-have skills
- Roadmap must NOT make nice-to-have skills sound like requirements
- `do_not_claim_until_completed` MUST be `true` if items are generated
