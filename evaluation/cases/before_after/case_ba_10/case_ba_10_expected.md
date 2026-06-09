# Expected Behavior — Before/After Case 10: Pure Keyword Stuffing

## Category
Keyword stuffing — many irrelevant skills added without evidence

## CV Summary (Base)
CV has relevant backend skills (FastAPI, PostgreSQL, Redis, Docker) but no Kubernetes or AWS. Gaps exist but evidence for existing skills is decent.

## CV Summary (Revised)
Revised CV is the WORST kind of keyword stuffing. It repeats "PostgreSQL and Redis and Docker and FastAPI" multiple times within the same bullet without adding any new project details, scope, or outcomes. Then it adds a long list of skills (Kubernetes, AWS, Celery, MongoDB, MySQL) with NO project evidence. This is textbook keyword stuffing.

## Expected Comparison Result
- base_score: ~58–72 (partial — basic evidence)
- new_score: ~55–78 (system gives partial credit for listed skills; stuffing may not be penalized enough)
- score_delta: -10 to +15 (near-zero or small — stuffing should not help much)
- resolved_missing_skills: empty (adding keywords to bullets is not real evidence)
- still_missing_skills: Redis, Kubernetes, AWS, testing (evidence still weak)
- keyword_stuffing_warnings: SHOULD fire for repeated keywords AND for skills without evidence
- improvement_summary: should explicitly warn about keyword stuffing pattern

## Score Components Expected
- Near-zero or small delta — keyword stuffing should NOT help the score
- keyword stuffing detection SHOULD fire strongly

## Guardrail Checks
- keyword_stuffing_warnings SHOULD contain warnings (repeated keywords + unverified skills)
- score_delta should be near zero or negative
- improvement_summary should explicitly mention keyword stuffing
