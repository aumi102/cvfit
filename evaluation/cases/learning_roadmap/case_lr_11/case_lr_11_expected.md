# Expected Behavior — Learning Roadmap Case 11: Must NOT Claim Skills Already Present

## CV Profile
All required skills are listed (FastAPI, PostgreSQL, Redis, Docker) BUT evidence is vague ("Did backend work", "Used some tech"). Kubernetes and AWS are listed but are nice-to-have.

## JD Profile
Backend engineer JD. Must-have: FastAPI, PostgreSQL, Redis, Docker. Nice-to-have: Kubernetes, AWS.

## Expected Learning Roadmap Output

### Observed System Behavior
The system treats skills listed in the skills section as "matched skills" (via ontology detection), even when project evidence is vague. As a result, when all required skills are listed, `build_learning_roadmap` returns an empty list.

### Must include
- Since the system detects FastAPI, PostgreSQL, Redis, Docker from the skills section as "matched", it may return 0 roadmap items

### Must NOT include
- ANY statement claiming "you already know FastAPI/Redis/Docker" in the `why` field
- `do_not_claim_until_completed: false`

## Critical Guardrail
The system must NOT say "you already know X" for skills that are only listed but not evidenced. This is the PRIMARY guardrail for this case. Note: the current implementation may not surface this issue because it produces 0 roadmap items when skills are listed — the system limitation is in not distinguishing "listed" from "evidenced".

## Guardrail Checks
- If roadmap is empty, the system is correctly identifying that no skills are "missing"
- `do_not_claim_until_completed` is not applicable when roadmap is empty
- The system limitation (not distinguishing listed vs evidenced) is acknowledged
