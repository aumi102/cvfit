# Expected Behavior — Before/After Case 08: Relevant Skill Added Without Real Evidence

## Category
Skill added but evidence is questionable

## CV Summary (Base)
CV is data-engineering focused. Strong Python, SQL, PostgreSQL, AWS. Missing FastAPI and Redis — both required by JD.

## CV Summary (Revised)
Revised CV adds FastAPI and Redis to skills list. BUT there is no project that demonstrates FastAPI or Redis usage. The "Personal Blog" project is completely unrelated. Adding skills to a skills list without corresponding project evidence is weak.

## Expected Comparison Result
- base_score: ~45–65 (partial — data engineering overlaps partially with backend)
- new_score: ~55–72 (slight improvement — skills listed but no real evidence)
- score_delta: +3 to +25 (small to moderate — system gives partial credit for skill listing)
- resolved_missing_skills: empty (FastAPI and Redis listed but no project evidence)
- still_missing_skills: FastAPI, Redis (no project evidence for them)
- keyword_stuffing_warnings: SHOULD fire for FastAPI/Redis (listed but not demonstrated)
- improvement_summary: should note that while FastAPI and Redis are listed, no project evidence was added

## Score Components Expected
- Small to moderate delta — adding skills to a list is not the same as demonstrating them
- keyword stuffing detection SHOULD fire

## Guardrail Checks
- keyword_stuffing_warnings SHOULD fire (FastAPI and Redis lack project evidence)
- improvement_summary must NOT say FastAPI and Redis gaps were fully resolved
- score_delta should be small to moderate
