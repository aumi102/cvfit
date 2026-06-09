# Expected Behavior — Before/After Case 01: Real Evidence Improvement

## Category
Score increase with real evidence (legitimate improvement)

## CV Summary (Base)
CV has FastAPI, PostgreSQL, Docker in skills but "Simple Blog API" project is too vague with no concrete backend details. Weak evidence for required skills.

## CV Summary (Revised)
Revised CV replaces vague project with "E-Commerce Product API" with specific FastAPI endpoints, PostgreSQL integration, Redis caching, and Docker deployment with health checks. Real evidence added.

## Expected Comparison Result
- base_score: ~55–72 (partial — weak evidence, system gives partial credit)
- new_score: ~70–88 (good — strong FastAPI, PostgreSQL, Redis, Docker evidence)
- score_delta: +10 to +35 (legitimate improvement)
- resolved_missing_skills: FastAPI, PostgreSQL, Redis (now have project evidence)
- still_missing_skills: empty (most required skills now matched)
- newly_matched_skills: Redis (from nice-to-have to matched)
- keyword_stuffing_warnings: empty (improvement is real, not stuffing)
- improvement_summary: should mention evidence improvement

## Score Components Expected
- Both versions have same skill list; revised has stronger project evidence
- keyword_stuffing_warnings must be empty — this is a genuine improvement

## Guardrail Checks
- improvement_summary must NOT say "all gaps resolved" if any gaps remain
- improvement_summary must NOT fabricate missing skills as resolved
- score_delta must be positive (improvement scenario)
