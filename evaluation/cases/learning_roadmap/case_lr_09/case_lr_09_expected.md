# Expected Behavior — Learning Roadmap Case 09: Massive Skill Gap Against Senior JD

## CV Profile
Extremely minimal CV. Only Python. No FastAPI, no PostgreSQL, no Redis, no Docker, no Kubernetes, no AWS, no security, no CI/CD. Massive gap against a senior JD.

## JD Profile
Senior backend engineer — maximum requirements. FastAPI, PostgreSQL, Redis, Docker, Kubernetes, AWS, API security, CI/CD all required.

## Expected Learning Roadmap Output
The `learning_roadmap` output must:

### Must include
- Roadmap items for all or most missing required skills
- `priority`: "high" for all (all are must-have for senior role)
- `why`: must honestly state that these are required by the JD but evidence was not found
- Topics should cover fundamental to advanced (this is a long learning journey)
- Mini projects should be realistic for the senior target level
- `do_not_claim_until_completed`: MUST be `true`

### Must NOT include
- Statements claiming the user is close to senior level
- Statements claiming the user already has senior skills
- Roadmap items that imply this is a short journey

## Guardrail Checks
- `do_not_claim_until_completed` MUST be `true`
- `why` must NOT claim user already has any of the missing skills
- The roadmap must be honest about the magnitude of the learning gap
