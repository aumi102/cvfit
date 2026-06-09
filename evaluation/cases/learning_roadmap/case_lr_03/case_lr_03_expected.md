# Expected Behavior — Learning Roadmap Case 03: Multiple Must-Have Gaps

## CV Profile
Very weak profile. Only Python. No FastAPI, no PostgreSQL, no Docker. All three are required for the junior role.

## JD Profile
Junior backend JD. FastAPI, PostgreSQL, Docker are all required.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Must include
- Roadmap items for: FastAPI, PostgreSQL, Docker (all missing)
- All items must have:
  - `priority`: "high" (all are must-have for this role)
  - `why`: must explain the skill is required by JD but not found in CV
  - `topics`: non-empty list appropriate for junior learning level
  - `mini_project`: appropriate for a junior developer's skill level
  - `cv_evidence_to_add_after_learning`: beginner-friendly guidance
  - `do_not_claim_until_completed`: MUST be `true`

### Must NOT include
- Roadmap items for skills already in CV (Python is matched)
- `do_not_claim_until_completed: false` for any skill
- Junior-level roadmap items for senior-level skills not in JD

## Guardrail Checks
- `do_not_claim_until_completed` MUST be `true` for ALL items
- `why` must NOT claim user already has these skills
- Topics and mini projects should be calibrated to junior level
