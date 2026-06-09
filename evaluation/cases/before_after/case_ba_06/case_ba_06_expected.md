# Expected Behavior — Before/After Case 06: Irrelevant Experience Added

## Category
Score should NOT increase significantly — irrelevant content added

## CV Summary (Base)
CV is a good match for the backend JD. FastAPI, PostgreSQL, Docker all present.

## CV Summary (Revised)
Revised CV adds unrelated "Team Leadership", "Marketing", "Event Planning" experience. These are NOT backend-relevant skills. The backend evidence remains unchanged.

## Expected Comparison Result
- base_score: ~55–75 (system may give partial credit even with vague evidence)
- new_score: ~55–78 (should NOT increase significantly — added content is irrelevant to JD)
- score_delta: -5 to +15 (near-zero or modest — irrelevant content should not help much)
- resolved_missing_skills: empty (no backend gaps were fixed)
- still_missing_skills: empty (no new gaps)
- newly_matched_skills: empty (added skills are not backend-related)
- keyword_stuffing_warnings: may contain warnings about irrelevant skills added
- improvement_summary: should note that added experience is not relevant to the JD

## Score Components Expected
- Near-zero or small delta expected — added content is irrelevant to backend JD
- system must NOT increase score dramatically just because more text was added

## Guardrail Checks
- score_delta should be modest (not dramatic)
- improvement_summary must NOT say backend gaps were resolved
- newly_matched_skills should be empty or not backend-related
