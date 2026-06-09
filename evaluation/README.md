# AI CV Fit — Evaluation Dataset

## Overview

This folder contains test cases for evaluating the quality and consistency of the AI CV Fit scoring system across Phase 1-4.

## Structure

```
evaluation/
  README.md              ← this file
  cases/
    easy/                ← 5 cases (high fit, clear alignment)          [Phase 1-3]
    medium/              ← 5 cases (partial mismatch, some relevance)      [Phase 1-3]
    hard/                ← 5 cases (weak alignment, role mismatch)       [Phase 1-3]
    edge/                ← 3 cases (extreme scenarios)                     [Phase 1-3]
    before_after/        ← 15 cases (comparison/revision scenarios)       [Phase 4]
    interview_prep/      ← 13 cases (interview question quality)         [Phase 4]
    learning_roadmap/    ← 13 cases (learning roadmap guardrails)        [Phase 4]
```

## Case Format

### Phase 1-3 Scoring Cases (cases/easy/, medium/, hard/, edge/)

Each case has three files:
- `case_XX_cv.txt` — CV text
- `case_XX_jd.txt` — Job description text
- `case_XX_expected.md` — Expected behavior, score range, and guardrail expectations

### Phase 4 Before/After Cases (cases/before_after/)

Each case has four files:
- `case_ba_XX_cv.txt` — Base (original) CV text
- `case_ba_XX_jd.txt` — Job description text
- `case_ba_XX_revised.txt` — Revised CV text (after user improvement)
- `case_ba_XX_expected.md` — Expected comparison result, score delta, and guardrail expectations

### Phase 4 Interview Prep Cases (cases/interview_prep/)

Each case has three files:
- `case_ip_XX_cv.txt` — CV text
- `case_ip_XX_jd.txt` — Job description text
- `case_ip_XX_expected.md` — Expected question types, required fields, and guardrail expectations

### Phase 4 Learning Roadmap Cases (cases/learning_roadmap/)

Each case has three files:
- `case_lr_XX_cv.txt` — CV text
- `case_lr_XX_jd.txt` — Job description text
- `case_lr_XX_expected.md` — Expected roadmap items, priority rules, and guardrail expectations

## Running the Evaluations

### Phase 1-3: Scoring Cases

```powershell
python scripts/evaluate_scoring_cases.py
python scripts/evaluate_scoring_cases.py --verbose
python scripts/evaluate_scoring_cases.py --case 01
python scripts/evaluate_scoring_cases.py --category easy
```

### Phase 4: Before/After Comparison

```powershell
python scripts/evaluate_comparison_cases.py
python scripts/evaluate_comparison_cases.py --verbose
python scripts/evaluate_comparison_cases.py --case ba_01
```

### Phase 4: Interview Prep

```powershell
python scripts/evaluate_interview_prep_cases.py
python scripts/evaluate_interview_prep_cases.py --verbose
python scripts/evaluate_interview_prep_cases.py --case ip_01
```

### Phase 4: Learning Roadmap

```powershell
python scripts/evaluate_roadmap_cases.py
python scripts/evaluate_roadmap_cases.py --verbose
python scripts/evaluate_roadmap_cases.py --case lr_01
```

### Run All Evaluations

```powershell
python scripts/evaluate_scoring_cases.py
python scripts/evaluate_comparison_cases.py
python scripts/evaluate_interview_prep_cases.py
python scripts/evaluate_roadmap_cases.py
```

### Run All Backend Tests

```powershell
cd backend
python -m pytest tests/test_phase4_outputs.py -v
python -m pytest tests/ -v
```

The first run may need to download or populate the local SentenceTransformers
model cache. After the model is cached, repeated runs should work without
another network fetch in the same environment.

## Case Naming Convention

The `case_XX_*` naming is intentional. The evaluation loaders discover
files by pattern, so do not rename them to generic names unless the script
is updated at the same time.

## Adding New Cases

### Phase 1-3 Scoring Cases

1. Create a new folder under `cases/easy/`, `medium/`, `hard/`, or `edge/`
2. Add `case_XX_cv.txt`, `case_XX_jd.txt`, `case_XX_expected.md`
3. Update case numbering sequentially
4. Run `evaluate_scoring_cases.py` to verify

### Phase 4 Before/After Cases

1. Create `evaluation/cases/before_after/case_ba_XX/`
2. Add `case_ba_XX_cv.txt`, `case_ba_XX_jd.txt`, `case_ba_XX_revised.txt`, `case_ba_XX_expected.md`
3. Update case numbering sequentially
4. Run `evaluate_comparison_cases.py` to verify

### Phase 4 Interview Prep Cases

1. Create `evaluation/cases/interview_prep/case_ip_XX/`
2. Add `case_ip_XX_cv.txt`, `case_ip_XX_jd.txt`, `case_ip_XX_expected.md`
3. Write expected question types and guardrail expectations in `case_ip_XX_expected.md`
4. Run `evaluate_interview_prep_cases.py` to verify

### Phase 4 Learning Roadmap Cases

1. Create `evaluation/cases/learning_roadmap/case_lr_XX/`
2. Add `case_lr_XX_cv.txt`, `case_lr_XX_jd.txt`, `case_lr_XX_expected.md`
3. Write expected roadmap items and guardrail expectations in `case_lr_XX_expected.md`
4. Run `evaluate_roadmap_cases.py` to verify

## Case Descriptions

### Phase 1-3 Scoring Cases (18 cases)

| Case | Category | CV Profile | JD Profile | Expected Score |
|------|----------|-----------|-----------|---------------|
| 01 | Easy | Backend dev with FastAPI, PostgreSQL, Redis, Docker | Backend Engineer with FastAPI, PostgreSQL, Redis, Docker | 70–85 |
| 02 | Easy | Full stack dev with Python, Flask, SQLite | Backend Developer with Python, Flask, SQL | 50–65 |
| 03 | Easy | Data engineer with Python, PostgreSQL, Docker, Kubernetes, GCP | Data Engineer | 68–78 |
| 04 | Easy | Junior dev with Python, Django, SQLite | Backend Developer | 50–65 |
| 05 | Easy | Senior dev with FastAPI, PostgreSQL, Redis, K8s, AWS | Senior Backend Engineer | 68–78 |
| 06 | Medium | Node.js dev, no Python | Backend Engineer (Python) | 50–65 |
| 07 | Medium | Data analyst with Python, pandas, SQL | Backend Engineer (FastAPI) | 48–60 |
| 08 | Medium | Frontend dev with basic Python scripts | Backend Engineer | 42–55 |
| 09 | Medium | DevOps engineer, strong Python, Docker, K8s, no API dev | Backend Engineer | 50–62 |
| 10 | Medium | ML engineer with Python, Flask, Docker | Backend Engineer | 45–58 |
| 11 | Hard | Ultra-vague CV, no specific tech | Senior Backend Engineer | 25–40 |
| 12 | Hard | Vague CV with Java, C++, generic language | Python Backend Engineer | 40–55 |
| 13 | Hard | Overqualified CV, too many irrelevant skills | Mid-Level Backend Engineer | 60–75 |
| 14 | Hard | Brief CV with minimal evidence | Backend Engineer | 50–62 |
| 15 | Hard | Cybersecurity specialist CV | Backend Engineer | 40–52 |
| 16 | Edge | Ultra-short CV (2 sentences) | Senior Backend Engineer | 30–42 |
| 17 | Edge | Ultra-long CV, ultra-short JD | Backend Engineer | 60–72 |
| 18 | Edge | CV listing everything with no evidence | Junior Backend Developer | 50–65 |

### Phase 4 Before/After Comparison Cases (15 cases)

| Case | Category | CV Profile | JD Profile | Expected Delta |
|------|----------|-----------|-----------|---------------|
| BA_01 | Real improvement | Weak FastAPI evidence → strong evidence | Backend Engineer | +15 to +25 |
| BA_02 | Real improvement | Flask/SQLite → FastAPI/PostgreSQL/K8s/AWS | Senior Backend Engineer | +20 to +35 |
| BA_03 | Real improvement | Frontend → targeted backend evidence | Backend Engineer | +10 to +25 |
| BA_04 | Real improvement | Django/SQLite → FastAPI/PostgreSQL/Docker | Backend Developer | +10 to +25 |
| BA_05 | Modest improvement | Already good → additional depth | Backend Engineer | +5 to +15 |
| BA_06 | Irrelevant content | Good backend CV + irrelevant skills | Backend Engineer | -5 to +5 |
| BA_07 | Weak evidence | Sparse CV → longer but shallow | Full Stack Developer | +5 to +20 |
| BA_08 | Questionable improvement | Data engineer → skill list only, no evidence | Backend Engineer | +3 to +15 |
| BA_09 | Keyword stuffing | Good CV + irrelevant tech list | Senior Backend Engineer | +3 to +15 |
| BA_10 | Pure stuffing | Good evidence → repeated keywords + skills | Backend Engineer | -5 to +5 |
| BA_11 | Fabrication | Minimal → fabricated "Google" experience | Junior Backend Developer | -5 to +10 |
| BA_12 | Real improvement | Flask/SQLite → FastAPI/PostgreSQL/Redis/Docker | Backend Engineer | +15 to +35 |
| BA_13 | Real improvement | Python only → all required skills with evidence | Backend Engineer | +25 to +55 |
| BA_14 | Real improvement | Mid-level → senior-level project | Senior Backend Engineer | +15 to +35 |
| BA_15 | Modest improvement | Good → additional real evidence | Backend Engineer | +3 to +12 |

### Phase 4 Interview Prep Cases (13 cases)

| Case | CV Profile | JD Profile | Expected Question Types |
|------|-----------|-----------|------------------------|
| IP_01 | Strong backend with metrics | Backend Engineer | project_deep_dive |
| IP_02 | No backend skills | Backend Engineer | gap_probe |
| IP_03 | Partial match — some present, some missing | Backend Engineer | project_deep_dive + gap_probe |
| IP_04 | All skills listed but evidence vague | Backend Engineer | project_deep_dive (acknowledge weak) |
| IP_05 | Junior level, learning | Junior Backend Developer | project_deep_dive + gap_probe (calibrated) |
| IP_06 | Relevant + irrelevant skills listed | Backend Engineer | project_deep_dive only (no irrelevant) |
| IP_07 | Senior level, deep evidence | Senior Backend Engineer | project_deep_dive (senior level) |
| IP_08 | Most skills missing | Junior Backend Developer | gap_probe (no project_deep_dive) |
| IP_09 | One skill missing | Backend Engineer | project_deep_dive + gap_probe |
| IP_10 | Strong match + auth + background tasks | Backend Engineer | project_deep_dive (multiple topics) |
| IP_11 | Extremely weak against senior JD | Senior Backend Engineer | gap_probe only |
| IP_12 | Perfect match | Backend Engineer | project_deep_dive |
| IP_13 | Good match + auth + background tasks | Backend Engineer | project_deep_dive |

### Phase 4 Learning Roadmap Cases (13 cases)

| Case | CV Profile | JD Profile | Key Guardrail |
|------|-----------|-----------|---------------|
| LR_01 | Multiple must-have gaps | Backend Engineer | do_not_claim_until_completed = true |
| LR_02 | One must-have gap (Redis) | Backend Engineer | Only 1 roadmap item |
| LR_03 | Multiple must-have gaps | Junior Backend Developer | Topics calibrated for junior |
| LR_04 | Skills listed but evidence vague | Backend Engineer | "Listed" ≠ "Evidenced" |
| LR_05 | Vague evidence for senior JD | Senior Backend Engineer | Senior-level calibration |
| LR_06 | All must-have matched, nice-to-have missing | Backend Engineer | Nice-to-have priority = medium |
| LR_07 | Only nice-to-have skills missing | Backend Developer | Nice-to-have priority = medium |
| LR_08 | Multiple nice-to-have missing | Backend Engineer | All nice-to-have priority = medium |
| LR_09 | Massive gap against senior JD | Senior Backend Engineer | Honest about magnitude |
| LR_10 | Junior level, multiple gaps | Junior Backend Developer | Beginner-friendly topics |
| LR_11 | Must NOT claim listed skills | Backend Engineer | No "already know" statements |
| LR_12 | Must NOT overstate nice-to-have | Backend Engineer | Nice-to-have ≠ must-have |
| LR_13 | Must NOT fabricate "already know" | Backend Developer | No fabricated past claims |

## Guardrail Checks

### Phase 1-3 Scoring Cases

Every case must pass these guardrail checks:

1. **No guarantee language** — output must not contain "guarantee hired", "will be hired", "will get the job", etc.
2. **Missing evidence wording** — missing skills must be phrased as "not found in parsed CV", not "you don't know X"
3. **No fabrication** — no invented skills, companies, years, metrics, certifications
4. **Conditional suggestions** — improvement suggestions must include "Only add this if it is true"
5. **Low-fit cap** — a CV with no relevant skills must not score 70+

### Phase 4 Before/After Cases

Every comparison case must pass these guardrail checks:

1. **No hiring guarantee language**
2. **Score delta appropriate** — stuffing/fabrication must not dramatically increase score
3. **Resolved skills require real evidence** — keyword listing alone is insufficient
4. **Keyword stuffing warnings fire** — when stuffing is detected
5. **Improvement summary honest** — acknowledges evidence quality, not just score

### Phase 4 Interview Prep Cases

Every interview prep case must pass these guardrail checks:

1. **project_deep_dive** only for skills with CV evidence
2. **gap_probe** for missing skills with honest answer outlines
3. **No fabrication** — answer outlines must not invent experience
4. **Question types valid** — only from allowed type set
5. **Required fields present** — question, type, why, outline, risk

### Phase 4 Learning Roadmap Cases

Every roadmap case must pass these guardrail checks:

1. **do_not_claim_until_completed = true** — mandatory for all items
2. **Why is future-facing** — never "you already know X"
3. **Priority correct** — high only for must-have missing
4. **No fabrication** — no "already know", "since you know" statements
5. **Estimated effort present** — required field

## Interpreting Results

The evaluation scripts compare actual system output against expected ranges. Any case that produces a score outside the expected range, or that fails guardrail checks, is flagged as a **discrepancy** for human review.

Exit code 0 = all cases passed. Exit code 1 = one or more cases failed.

## Backend Tests

Phase 4 backend tests are in:

```
backend/tests/test_phase4_outputs.py
```

This file contains 57 tests covering:
- Result JSON v3 schema and required fields
- Improvement Action Plan safety
- Safe Rewrite Suggestions guardrails
- Interview Prep quality
- Learning Roadmap guardrails
- Comparison engine correctness
- Keyword Stuffing detection
- Sensitive data scrubbing
- Guardrail v2 compliance

Run with:

```powershell
cd backend
python -m pytest tests/test_phase4_outputs.py -v
```
