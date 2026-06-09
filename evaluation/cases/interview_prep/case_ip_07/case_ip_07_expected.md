# Expected Behavior — Interview Prep Case 07: Senior Profile With Deep Project Evidence

## CV Profile
Senior-level profile with extensive production evidence. All required skills have detailed project evidence with metrics, scale, and architectural decisions. This is a high-quality CV.

## JD Profile
Senior backend engineer JD requiring deep technical knowledge across all areas.

## Expected Interview Prep Output
The `interview_prep` output must:

### Must include
- Multiple `project_deep_dive` questions about the Payment Gateway project
- Questions covering PostgreSQL (ACID, row-level locking), Redis (caching, uptime), Kubernetes (auto-scaling, deployments), AWS (EKS), security (JWT, OAuth2, RBAC)
- At least 1 question referencing specific evidence from the Payment Gateway project
- `risk_if_user_cannot_answer` for deep technical questions should reflect the senior level
- `why_this_question` should explain the production-scale relevance

### Must NOT include
- Questions about skills not in CV or JD
- Questions that probe basic concepts (for a senior profile, basic questions are inappropriate)
- Questions that fabricate architectural details not in the CV

## Guardrail Checks
- `project_deep_dive` questions must reference specific Payment Gateway evidence
- Answer outlines must NOT invent requirements or scale claims not in the CV
- Questions must be calibrated to senior level (not junior level)
