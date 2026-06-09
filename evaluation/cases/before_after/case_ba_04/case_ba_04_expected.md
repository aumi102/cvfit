# Expected Behavior — Before/After Case 04: Incremental Skill Addition

## Category
Score increase with targeted new evidence

## CV Summary (Base)
CV has Django, SQLite, Python. Django is acceptable (JD says FastAPI or Flask or Django). SQLite is weaker than PostgreSQL. Minimal evidence depth.

## CV Summary (Revised)
Revised CV adds FastAPI + PostgreSQL + Docker with a specific healthcare API project. Evidence is concrete and relevant.

## Expected Comparison Result
- base_score: ~50–70 (partial — Django acceptable but SQLite is weak; system may give partial credit)
- new_score: ~70–88 (good — FastAPI, PostgreSQL, Docker all matched with real evidence)
- score_delta: +10 to +35 (legitimate improvement)
- resolved_missing_skills: PostgreSQL, Docker (now matched)
- still_missing_skills: empty or minimal
- keyword_stuffing_warnings: empty
- improvement_summary: should reflect FastAPI + PostgreSQL + Docker improvement

## Guardrail Checks
- Both scores must be within expected bounds
- improvement_summary must NOT claim Django was fixed (Django was already matching)
- score_delta must be positive
