# Phase 3 Demo Checklist

Use synthetic CV/JD data only. Do not use real candidate documents in demos.

## Setup

- Confirm the API and worker are deployed or running locally.
- Confirm the frontend points to the intended backend.
- Run strict smoke when possible:

```powershell
$env:API_BASE_URL="https://cvfit.onrender.com"
$env:SMOKE_ALLOW_MUTATING="1"
$env:REQUIRE_RESULT_V2="1"
python scripts/smoke_test_mvp.py --mutating
```

## Core Flow

- Log in or create a demo account.
- Upload a synthetic CV.
- Paste a synthetic job description.
- Start analysis and wait for completion.
- Confirm the Result Dashboard v2 opens without raw JSON.
- Confirm the dashboard shows:
  - overall score
  - fit level
  - score breakdown
  - matched skills
  - missing skills
  - CV/JD evidence snippets
  - improvement actions
  - limitations/disclaimer
  - DOCX report download
- Download the DOCX report and confirm it includes score breakdown, evidence, gaps, actions, and limitations.
- Open history and confirm the completed job appears with score and report status.

## Scenario Coverage

- High-fit case: use an easy evaluation case such as `evaluation/cases/easy/case_01` to show strong matched skills and evidence.
- Partial/medium case: use a medium evaluation case such as `evaluation/cases/medium/case_08` to show mixed coverage and actionable gaps.
- Unrelated low-fit case: use a hard or edge case such as `evaluation/cases/hard/case_11` or an unrelated synthetic CV to show a low score and missing evidence.

## Trust Narrative

Explain why Phase 3 is more trustworthy than a keyword checker:

- The score is broken into multiple components instead of one opaque number.
- Matched skills are tied to evidence snippets from the parsed CV/JD.
- Missing skills are phrased as missing evidence, not absolute claims about the candidate.
- Improvement actions are conditional and include no-fabrication guardrails.
- The DOCX report repeats the same structured result for review outside the app.
- The evaluation suite checks expected score ranges, fit levels, low-fit behavior, and no hiring-guarantee wording.

## Do Not Demo

- Do not claim the score guarantees interviews, offers, or hiring outcomes.
- Do not present suggestions as permission to invent skills or experience.
- Do not expose access tokens, JWTs, storage paths, S3 keys, or raw private CV text.
- Do not use production candidate data.
