# Expected Behavior — Learning Roadmap Case 10: Junior Gap — Topics and Projects Must Be Beginner-Friendly

## CV Profile
Very minimal. Only Python. No FastAPI, no PostgreSQL, no Docker, no tests. All are required for junior role.

## JD Profile
Junior backend developer JD — beginner-friendly requirements. "Basics" level for PostgreSQL and Docker.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Must include
- Roadmap items for: FastAPI, PostgreSQL, Docker
- `priority`: "high" (all required for junior role)
- `why`: must explain why each skill is needed for this junior role
- `topics`: beginner-friendly learning paths (not advanced topics)
- `mini_project`: simple, achievable project appropriate for a beginner
- `estimated_effort`: reasonable for junior learning (not "6 months")
- `cv_evidence_to_add_after_learning`: beginner-appropriate guidance
- `do_not_claim_until_completed`: MUST be `true`

### Must NOT include
- Advanced topics (e.g., Kubernetes for a junior JD)
- Senior-level project suggestions
- Estimates suggesting "expert level" in short time
- `do_not_claim_until_completed: false`

## Guardrail Checks
- Topics and projects must be calibrated to beginner level
- `do_not_claim_until_completed` MUST be `true`
- `estimated_effort` should be realistic for a junior developer
