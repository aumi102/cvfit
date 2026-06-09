# Expected Behavior — Learning Roadmap Case 13: Must NOT Fabricate "Already Know" Statements

## CV Profile
Has Python and PostgreSQL with some evidence. Missing FastAPI (must-have), Redis (must-have), Docker (must-have), Kubernetes (nice-to-have), AWS (nice-to-have).

## JD Profile
Backend developer JD. Must-have: Python, FastAPI, PostgreSQL, Redis, Docker. Nice-to-have: Kubernetes, AWS.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Must include
- Roadmap items for: FastAPI, Redis, Docker (all must-have)
- `priority`: "high" for must-have skills
- `why`: must honestly explain that these skills are required by the JD but evidence was not found in the CV
- `topics`: appropriate learning topics for each skill
- `mini_project`: concrete project suggestions for each skill
- `cv_evidence_to_add_after_learning`: specific guidance on what to add after learning
- `do_not_claim_until_completed`: MUST be `true`
- Roadmap items for nice-to-have (Kubernetes, AWS) with "medium" priority if included

### Must NOT include
- ANY statement claiming "you already know FastAPI/Redis/Docker"
- ANY statement claiming "since you know Python, FastAPI is easy"
- Roadmap items that bypass the learning requirement for any skill
- `do_not_claim_until_completed: false` for any skill

## Critical Guardrail
The system must NEVER fabricate statements implying the user already has a skill they do not have evidence for. This is the core learning roadmap guardrail.

## Guardrail Checks
- `do_not_claim_until_completed` MUST be `true` for ALL items
- `why` must NOT contain "you already know" or "since you know" for missing skills
- Priority must be "high" for must-have missing skills
- Nice-to-have skills must have "medium" priority
