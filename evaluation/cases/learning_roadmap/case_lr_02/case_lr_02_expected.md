# Expected Behavior — Learning Roadmap Case 02: One Must-Have Skill Missing

## CV Profile
Good backend profile. FastAPI, PostgreSQL, Docker all present with project evidence. Redis is the ONLY gap — it is explicitly required by the JD but absent from CV.

## JD Profile
Standard backend JD with Redis as a required skill.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Must include
- Exactly 1 roadmap item: Redis
- The Redis item must have:
  - `skill`: "Redis" (or similar)
  - `priority`: "high" (Redis is required by JD)
  - `why`: explains that Redis is required by JD but not found in CV
  - `topics`: non-empty list (Redis basics, caching, key expiry)
  - `mini_project`: specific project suggestion
  - `cv_evidence_to_add_after_learning`: future-facing guidance
  - `do_not_claim_until_completed`: MUST be `true`

### Must NOT include
- Roadmap items for FastAPI, PostgreSQL, Docker (already matched)
- `do_not_claim_until_completed: false`
- Any statement implying user already has Redis knowledge

## Guardrail Checks
- Only 1 roadmap item (Redis is the only missing must-have)
- `do_not_claim_until_completed` MUST be `true`
- `why` must NOT say "since you already know Redis"
