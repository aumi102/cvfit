# Expected Behavior — Interview Prep Case 10: Strong Match With Background Tasks and Auth

## CV Profile
Excellent match for the JD. All required skills present with detailed SaaS project evidence. Strong coverage of background tasks (Celery) and authentication (JWT).

## JD Profile
Backend engineer requiring FastAPI, PostgreSQL, Redis, Docker, background task processing, API authentication.

## Expected Interview Prep Output
The `interview_prep` output must:

### Must include
- Multiple `project_deep_dive` questions about the SaaS Platform project
- Questions covering: multi-tenant PostgreSQL, Redis (session + rate limiting), Celery background tasks, JWT authentication
- At least 1 question referencing Celery/Redis queue (background tasks)
- At least 1 question referencing JWT authentication

### Must NOT include
- Questions about skills not in JD (e.g., Kubernetes, AWS, GraphQL)
- Questions that fabricate multi-tenant or security requirements not in the CV
- Basic questions when the CV shows senior-level work

## Guardrail Checks
- Questions must reference specific SaaS Platform evidence
- Answer outlines must NOT invent architectural decisions not in the CV
- No questions about irrelevant skills
