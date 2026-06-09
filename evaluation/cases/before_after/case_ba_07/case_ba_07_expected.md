# Expected Behavior — Before/After Case 07: CV Made Longer But Evidence Still Weak

## Category
Score increases but evidence is still shallow — keyword stuffing concern

## CV Summary (Base)
CV is extremely sparse. Only Python mentioned, no framework, no database, no deployment. Very weak for full stack JD.

## CV Summary (Revised)
Revised CV adds React, Node.js, PostgreSQL, Docker but each is mentioned without concrete project evidence. Bullets are short and vague ("Built React web applications" without specifics). Added "Machine Learning, AI, Blockchain, Web3" — these are keyword stuffing, not real evidence.

## Expected Comparison Result
- base_score: ~20–50 (weak — extremely sparse)
- new_score: ~40–82 (system may give partial credit for listed skills even without evidence)
- score_delta: +5 to +50 (system gives partial credit for skill listing; this is a KNOWN LIMITATION)
- resolved_missing_skills: empty or limited (skills listed but evidence is weak)
- still_missing_skills: may remain (evidence quality is low)
- keyword_stuffing_warnings: SHOULD contain warnings about ML/AI/Blockchain/Web3 listing
- improvement_summary: should note that while skills are listed, evidence quality is still weak

## Score Components Expected
- Large delta may occur — this exposes a system limitation where skill listing gets partial credit
- keyword stuffing detection MUST fire for the irrelevant tech additions
- NOTE: If keyword stuffing detection fails, this case will show a large delta. This is expected behavior given current system limitations.

## Guardrail Checks
- keyword_stuffing_warnings SHOULD fire (ML/AI/Blockchain should be flagged)
- improvement_summary must NOT say evidence is strong
- This case may fail on delta range due to system giving partial credit for listed skills
