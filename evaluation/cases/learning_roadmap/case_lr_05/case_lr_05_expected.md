# Expected Behavior — Learning Roadmap Case 05: Vague Evidence for Senior JD

## CV Profile
CV lists all the required skills (FastAPI, PostgreSQL, Redis, Docker, Kubernetes, AWS) BUT the project descriptions are vague ("Built backend APIs", "Used databases", "Deployed with containers"). Cannot determine depth or experience level.

## JD Profile
Senior backend engineer JD with high requirements: FastAPI, PostgreSQL, Redis, Docker, Kubernetes, AWS, API security.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Observed System Behavior
The system treats skills listed in the skills section as "matched skills" (via ontology detection), even when project evidence is vague. Since all required skills are listed, the system produces 0 roadmap items.

### Must include
- Roadmap items are based on `missing_skills` list — if all skills are listed, no roadmap items

### Must NOT include
- Statements claiming the user has senior-level experience
- `do_not_claim_until_completed: false`

## Guardrail Checks
- The system must distinguish "listed" from "evidenced" — the current implementation does not, which is a system limitation
- This case exposes the limitation: skills listed without evidence still get roadmap items
- `do_not_claim_until_completed` would be `true` if items were generated
