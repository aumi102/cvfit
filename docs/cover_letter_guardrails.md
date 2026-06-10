# Cover Letter Guardrails — Phase 5

**Version:** 1.0
**Date:** 2026-06-10
**Owner (backend):** Phúc
**Owner (evaluation/QA):** Đạt
**Status:** Contract only — no implementation in this PR
**Extends:** Guardrails v2 (Phase 4), Guardrails v3 (Phase 5)

---

## A. Scope

**Cover Letter Draft v1** is a single-pass AI-assisted draft generation feature.

Key constraints:

- Output is explicitly labeled as a **draft**. It is not a final, guaranteed application letter.
- The user must review and edit the draft before submitting it to any employer.
- Every generated draft includes review notes explaining assumptions and missing evidence.
- This feature is not a "CV ghostwriter" — it cannot generate claims the user cannot verify in a real interview.

---

## B. Inputs

The cover letter generator must receive and use all of the following inputs when available:

| Input | Required | Source |
|---|---|---|
| `jd_text` | Required | Application workspace `jd_text` |
| `cv_evidence` | Required | Analysis result: matched skills, CV bullets, parsed evidence |
| `matched_skills` | Required | Analysis result: `matched_skills` list |
| `missing_skills` | Required | Analysis result: `missing_skills` list |
| `profile_items` | Optional | Career profile / evidence vault items (skills, projects, experience, etc.) |
| `readiness_summary` | Optional | Application readiness summary if available |
| `job_title` | Optional | Application workspace `job_title` |
| `company_name` | Optional | Application workspace `company_name` (nullable) |

If `company_name` is null or missing, the generator must use neutral, role-focused wording instead of referencing a specific company.

---

## C. Required Cover Letter Structure

Every generated cover letter draft must contain all of these sections:

```text
Opening
  — Introduce the applicant and the role they are applying for.
  — Do not invent personal details not present in CV/profile.

Why This Role / Company
  — Explain why the applicant is interested in this type of role.
  — If company_name is available, reference publicly known company context only.
  — If company_name is missing, use role-focused motivation from JD.
  — Do not fabricate company knowledge or invent cultural fit claims.

Relevant Evidence From CV / Profile
  — Highlight 2–4 specific evidence items from matched CV/profile.
  — Each item must be traceable to a matched skill, CV bullet, or profile item.
  — Do not include skills that are only in the JD but not in the CV/profile.

Contribution Fit
  — Describe how the applicant's existing evidence aligns with the JD requirements.
  — Use conditional language for areas where evidence is partial or missing.
  — Do not convert a missing skill into a claimed competency.

Closing
  — Express genuine interest in discussing further.
  — Do not promise hiring success or outcomes.

Review Notes / Needs User Review
  — List all assumptions made during generation.
  — List all missing evidence items the user should address before sending.
  — Explicitly state the draft needs user review.
```

---

## D. Hard Guardrails

The following behaviors are **always prohibited** in generated cover letters:

### Fabrication Prohibition

- Do **not** fabricate skills, companies, projects, work experience, certifications, achievements, metrics, education, or external links.
- Do **not** claim direct experience unless it appears in CV evidence or profile items.
- Do **not** convert a JD-only skill (appears in JD but not in CV/profile) into a claimed competency.
- Do **not** invent company names, team names, product names, or employer names not in the CV.
- Do **not** invent metrics, percentages, or impact numbers not present in CV evidence.

### Missing Skill Prohibition

- Do **not** write "I am proficient in Kubernetes" when Kubernetes only appears in the JD.
- Do **not** write "My Kubernetes expertise..." if there is no Kubernetes evidence.
- Instead: "The JD highlights Kubernetes as a key requirement. I am actively building expertise in this area." — only if the user has indicated learning intent in their profile.

### No Guarantee Language

- Do **not** promise hiring, interview invitation, or selection outcomes.
- Do **not** write "I guarantee I will contribute immediately" or similar.

### Company Name Safety

- If `company_name` is null or empty, use "this role" or "your team" instead of a company name.
- Do **not** invent a company name or use a placeholder like "[Company]" that the user might forget to replace — use neutral role-based wording instead.

### Weak Evidence Handling

- If the matched CV evidence for a claimed skill is weak (skills-section only, no project detail), mark it explicitly in `review_notes`.
- Do **not** present weak evidence as strong backing.

### Privacy and Security

- Do **not** include JWT, access tokens, storage keys, raw CV text, or internal system paths in the output.
- Do **not** include other users' data or analysis results.

---

## E. Safe Wording Examples

These phrasings are acceptable:

```text
"My background includes hands-on experience with FastAPI, as demonstrated in my e-commerce API project."
"I have worked on backend systems using PostgreSQL and Redis, as outlined in my CV."
"Based on my CV evidence, I can highlight my experience in building REST APIs and managing relational databases."
"I would like to further discuss how my experience aligns with your team's needs."
"This draft needs review because my Docker experience is limited to personal projects — please verify before sending."
"I am currently building expertise in Kubernetes, which is listed as a requirement for this role."
```

---

## F. Unsafe Wording Examples

These phrasings are **prohibited**:

```text
"I led the platform migration at Acme Corp."
  → Fabricated: company name not in CV.

"I am an expert in Kubernetes."
  → Fabricated: Kubernetes only in JD, not in CV.

"I increased revenue by 40% in my previous role."
  → Fabricated: metric not in CV evidence.

"I guarantee I will deliver results from day one."
  → Prohibited hiring guarantee.

"With my 5 years of experience in machine learning..."
  → Fabricated: years of experience not in CV.

"[Company Name] seems like the perfect fit for my skills."
  → Placeholder that will be sent if user forgets to replace it.
```

---

## G. Output Schema Proposal

```json
{
  "opening": "",
  "why_role_company": "",
  "relevant_evidence": [
    {
      "evidence_item": "",
      "source": "cv_bullet | profile_item | matched_skill",
      "cv_reference": ""
    }
  ],
  "contribution_fit": "",
  "closing": "",
  "review_notes": [
    "Assumption: company_name was not provided; role-focused wording used.",
    "Assumption: Docker experience sourced from skills section only — no project evidence found."
  ],
  "missing_evidence": [
    "Kubernetes: required by JD but not found in CV or profile."
  ],
  "disclaimer": "This is a draft cover letter generated from your CV and job description. It must be reviewed and edited before submission. It does not guarantee any hiring outcome."
}
```

| Field | Required | Notes |
|---|---|---|
| `opening` | Yes | |
| `why_role_company` | Yes | |
| `relevant_evidence` | Yes | List with at least 1 item; each item traceable to evidence |
| `contribution_fit` | Yes | |
| `closing` | Yes | |
| `review_notes` | Yes | Non-empty; at least one note about assumptions or missing evidence |
| `missing_evidence` | Yes | May be empty list if all JD requirements are covered by evidence |
| `disclaimer` | Yes | Exact wording required |

---

## H. Evaluation Checklist

Cases Đạt must cover in the evaluation skeleton (PR2):

| Case | Expected Behavior |
|---|---|
| **Good evidence case** | Matched skills + project evidence → `relevant_evidence` references CV items; `review_notes` minimal |
| **Weak evidence case** | Skills in CV skills section but no project detail → `review_notes` flags weak evidence; does not present as strong |
| **Missing skill case** | JD requires Kubernetes, not in CV → `missing_evidence` includes Kubernetes; body does not claim Kubernetes experience |
| **Hallucination-risk case** | JD requires experience at a specific company type → body does not invent company context; `review_notes` notes assumption |
| **Irrelevant CV/JD case** | CV is for marketing but JD is for backend engineering → `review_notes` flags high mismatch; `missing_evidence` lists critical gaps; body does not fabricate technical experience |
