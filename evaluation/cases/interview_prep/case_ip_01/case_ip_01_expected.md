# Expected Behavior — Interview Prep Case 01: Strong Match, Deep Project Evidence

## CV Profile
Strong backend evidence with specific project details. FastAPI, PostgreSQL, Redis, Docker all have concrete project evidence with metrics.

## JD Profile
Standard backend engineer JD requiring FastAPI, PostgreSQL, Redis, Docker.

## Expected Interview Prep Output
The `interview_prep` output must contain questions that:

### Must include
- At least 1 `project_deep_dive` question about the E-Commerce Product API
- The question must reference FastAPI, PostgreSQL, or Redis (all are in CV and JD)
- The question must include `related_cv_evidence` referencing the relevant project
- The question must include `related_jd_requirement` referencing the JD requirement
- The question must include `why_this_question` explaining relevance
- The question must include `risk_if_user_cannot_answer` with a meaningful risk

### Must NOT include
- Questions about skills not in CV (e.g., Kubernetes, AWS, GraphQL)
- Questions about skills not in JD
- Questions that fabricate project details not in CV

## Required Fields per Question
```
type: project_deep_dive
related_cv_evidence: non-empty list (must reference the E-Commerce project)
related_jd_requirement: non-empty string (JD requirement text)
why_this_question: non-empty string
risk_if_user_cannot_answer: non-empty string
```

## Guardrail Checks
- Questions must NOT ask about unmentioned technologies (no AWS if not in CV)
- Questions must NOT fabricate project requirements not in the CV evidence
- Answer outlines must NOT include invented facts
