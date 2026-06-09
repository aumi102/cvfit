# Expected Behavior — Before/After Case 11: CV Longer With Fabricated Experience

## Category
FABRICATION — CV adds completely fabricated experience

## CV Summary (Base)
CV is extremely minimal. Only Python. Very weak for the JD.

## CV Summary (Revised)
FABRICATION ALERT: The revised CV fabricates "5 years at Google as senior engineer", "100 million users", "Led team of 10", "multi-million dollar project". These are completely fabricated claims. Adding length does NOT make this a legitimate CV.

## Expected Comparison Result
- base_score: ~20–65 (system may give partial credit for skill listing even without evidence)
- new_score: ~25–80 (system may give partial credit for listed skills; fabrications may get some credit)
- score_delta: -5 to +25 (system gives partial credit for listing skills even without evidence — this is a KNOWN SYSTEM LIMITATION)
- resolved_missing_skills: empty (fabricated skills should NOT be treated as resolved)
- still_missing_skills: FastAPI, PostgreSQL, Docker (fabrications are not real evidence)
- keyword_stuffing_warnings: SHOULD fire for vague mega-scale claims
- improvement_summary: should note that the CV added unverifiable fabrications, NOT real evidence

## Critical Guardrail
This case is a FABRICATION test. The system must:
- NOT treat fabricated experience as real evidence
- NOT list "Google", "senior engineer", "100 million users" as resolved gaps
- Score should NOT jump dramatically (but partial credit for skill listing may occur — this is a system limitation)

## Guardrail Checks
- improvement_summary must NOT say gaps were resolved with fabricated evidence
- resolved_missing_skills must NOT include fabricated skills
- system must NOT say "the CV improved significantly" when it contains fabrications
- NOTE: Large delta may occur due to system giving partial credit for listed skills — this is a known system limitation
