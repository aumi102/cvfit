# Expected Behavior — Before/After Case 15: Modest Improvement on Already-Good CV

## Category
Small score increase — already good CV, adds more evidence

## CV Summary (Base)
CV is already a solid match. FastAPI, PostgreSQL, Redis, Docker all present. This is already a good-fit CV.

## CV Summary (Revised)
Revised CV adds "Real Estate Listing API" with full-text search, Nginx, and pytest. Additional evidence is real and relevant, but the base CV was already well-matched. This is a modest improvement scenario.

## Expected Comparison Result
- base_score: ~65–82 (good — already well-matched; system may give partial credit)
- new_score: ~72–90 (good to excellent — additional evidence adds depth)
- score_delta: +3 to +20 (modest improvement — base was already good)
- resolved_missing_skills: empty (base was already well-matched)
- still_missing_skills: empty or minimal
- keyword_stuffing_warnings: empty (evidence is real)
- improvement_summary: should note that additional real evidence was added, strengthening an already solid CV

## Score Components Expected
- Small to moderate positive delta expected — base was already good
- system must NOT give huge delta just because more bullets were added

## Guardrail Checks
- score_delta should be modest (3-20 points), not dramatic
- keyword_stuffing_warnings must be empty
- improvement_summary must NOT claim major gaps were fixed
