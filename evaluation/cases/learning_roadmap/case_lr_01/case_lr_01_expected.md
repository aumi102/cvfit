# Expected Behavior — Learning Roadmap Case 01: Multiple Must-Have Gaps

## CV Profile
CV has Python and Flask. Missing FastAPI (preferred), PostgreSQL (must-have), Redis (must-have), Docker (must-have). Multiple critical gaps.

## JD Profile
Standard backend engineer JD with FastAPI, PostgreSQL, Redis, Docker as requirements.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Must include
- Roadmap items for: FastAPI, PostgreSQL, Redis, Docker (all missing from CV)
- All 4 items must have:
  - `skill`: correct skill name
  - `priority`: "high" (all are required by JD)
  - `why`: explains why this skill is needed based on JD requirement
  - `topics`: non-empty list of learning topics
  - `mini_project`: non-empty specific project suggestion
  - `cv_evidence_to_add_after_learning`: future-facing guidance
  - `do_not_claim_until_completed`: MUST be `true`

### Must NOT include
- `do_not_claim_until_completed: false` for any skill
- Statements that imply the user already has FastAPI/PostgreSQL/Redis/Docker
- Statements like "since you already know X, learn Y" when X is missing
- Roadmap items for skills that are already matched in CV

## Critical Guardrail Check
- `do_not_claim_until_completed` MUST be `true` for ALL items (this is the most important guardrail)
- `why` must be future-facing ("the JD mentions X, but evidence was not found"), NOT present ("you know X")
