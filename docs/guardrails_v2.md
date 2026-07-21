# Guardrails v2 — AI CV Fit Phase 4

**Version:** 2.0
**Date:** 2026-06-09
**Owner:** Đạt
**Status:** Active — Phase 4
**Extends:** Guardrails v1.5 (Phase 3)

---

## Purpose

This document extends Guardrails v1.5 with Phase 4-specific rules for Result JSON v3, Improvement Action Plan, Safe CV Rewrite, Interview Prep, Learning Roadmap, Before/After Comparison, and Keyword Stuffing Detection. It is the authoritative guardrail reference for Phase 4 development and evaluation.

---

## Guardrail Philosophy

> The system must **never fabricate** a skill, experience, company, metric, or certification. The system must **always distinguish** between evidence found in the CV and inference from context. All suggestions must be **conditional**. Missing evidence must be described as evidence not found, not as proof the candidate lacks the skill.

---

## 1. Result JSON v3 Guardrails

### 1.1 — No Hiring Guarantee

Every result JSON v3 must contain the following limitation:

```
"This analysis estimates CV-to-JD fit only and does not guarantee any hiring outcome."
```

The system must **never** produce output containing:

```
"you are guaranteed to be hired"
"you will definitely get the job"
"guaranteed an interview"
"this will result in hiring"
"100% sure to be hired"
"you will definitely be selected"
```

### 1.2 — v3 Required Fields

Every Result JSON v3 must contain these additive fields:

| Field | Type | Description |
|---|---|---|
| `schema_version` | string | Must be `"3.0"` |
| `improvement_actions` | list | Up to 8 prioritized actions |
| `safe_rewrite_suggestions` | list | Up to 4 safe rewrite templates |
| `interview_prep` | list | Up to 6 interview questions |
| `learning_roadmap` | list | Up to 6 roadmap items |
| `limitations` | list | Must include the no-guarantee notice |
| `metadata` | dict | Must include `contract_version` and `scorer_version` |

### 1.3 — v2 Compatibility

Result JSON v3 must preserve all v2 fields and aliases:

| v2 Alias | v3 Equivalent |
|---|---|
| `overall_fit_score` | `result.overall.fit_score` |
| `result.fit_score` | `result.fit_score` |
| `result.scores.fit_score` | `result.scores.fit_score` |

---

## 2. Improvement Action Plan Guardrails

### 2.1 — Mandatory `do_not_fabricate` Field

Every improvement action **must** include:

```
"do_not_fabricate": true
```

This field is **mandatory** and must be `true` for every action. Actions that suggest CV changes must never set this to `false`.

### 2.2 — Conditional Wording

Every improvement action `safe_suggestion` must use conditional wording:

```
"If you have actually used {skill}, add a truthful CV bullet with project context..."
"Only add this if it is true."
```

### 2.3 — Priority Mapping

| Missing Skill Type | Action Priority |
|---|---|
| `must_have` missing | `high` |
| `nice_to_have` missing | `medium` |
| CV quality issue | `medium` or `low` |

### 2.4 — No Fabrication Instruction

Improvement actions must **never** instruct the user to fabricate:

```
✗  "Add 3 years of FastAPI experience."
✗  "Claim you built a production API for 10M users."
✗  "Say you worked at a big tech company."
✓  "If you have FastAPI experience, describe the API endpoints you built."
✓  "Only add this if it is true."
```

---

## 3. Safe CV Rewrite Guardrails

### 3.1 — Template, Not Finished Claim

Safe rewrite suggestions must be **templates with placeholders**, not finished claims:

```
✓  "Built [actual feature] using [actual framework] and [actual database]..."
✗  "Built a FastAPI API with PostgreSQL to serve 1M users."
```

The system must **never** produce a finished rewrite bullet with specific numbers, companies, or claims not present in the CV.

### 3.2 — Mandatory Warning Field

Every safe rewrite suggestion **must** include a `warning` field with content that:

- Reminds the user to use only true details
- Explains the risk of adding fabricated content

Example:

```
"Only use details that are true and can be defended in an interview."
```

### 3.3 — `missing_context_to_confirm` Field

Every safe rewrite suggestion **must** include a `missing_context_to_confirm` list identifying what the user must verify before using the suggestion.

Required context items:

```
"actual feature or workflow"
"actual framework"
"actual database"
"real metric or actual outcome"
```

### 3.4 — `do_not_fabricate: true`

Every safe rewrite suggestion must include:

```
"do_not_fabricate": true
```

---

## 4. Interview Prep Guardrails

### 4.1 — Question Types

Valid `type` values:

| Type | When to Use |
|---|---|
| `technical` | Skills in both CV and JD |
| `behavioral` | Soft skills relevant to JD |
| `project_deep_dive` | Project evidence in CV matches JD |
| `gap_probe` | Skill is in JD but missing from CV |
| `system_design` | Senior-level architecture questions |

### 4.2 — `project_deep_dive` Rules

A `project_deep_dive` question is only appropriate when:

- The skill appears in **both** the CV and the JD
- There is **CV evidence** (bullet, project description) supporting the skill
- The question asks about **specific evidence** from the CV, not invented requirements

A `project_deep_dive` question must **NOT** be generated for:

- Skills listed in the skills section but with **no project evidence**
- Skills **not mentioned** in the JD
- Skills the candidate clearly does not have

### 4.3 — `gap_probe` Rules

A `gap_probe` question is appropriate when:

- A skill is required by the JD but **not found in the CV**
- The question helps the candidate **honestly prepare** for the gap

A `gap_probe` question must:

- Include `related_cv_evidence`: `[]` or `null` (no evidence exists)
- Include `why_this_question` explaining the gap
- Have an answer outline that recommends **honest preparation**, not fabrication

### 4.4 — `risk_if_user_cannot_answer` Rules

Every interview question must include a meaningful `risk_if_user_cannot_answer` field that:

- Explains the consequence of not being able to answer
- Does **not** fabricate the consequence

### 4.5 — No Protected Information

Questions must **never** ask about:

- Gender, age, religion, ethnicity, family status
- Medical information
- Political views
- Information not relevant to the job

### 4.6 — Answer Outlines

`suggested_answer_outline` must:

- Be a non-empty list of bullet points
- Include **only guidance**, not fabricated answers
- Encourage the user to share **real** experience, not invented claims

---

## 5. Learning Roadmap Guardrails

### 5.1 — `do_not_claim_until_completed` is Mandatory and Must Be `true`

Every learning roadmap item **must** include:

```
"do_not_claim_until_completed": true
```

This field is **mandatory**. The system must **never** imply the user has already completed or learned a skill that is missing from their CV.

### 5.2 — Roadmap is Future-Facing

The `why` field must be **future-facing**, not past-claiming:

```
✓  "The JD mentions FastAPI, but FastAPI evidence was not found in the parsed CV."
✓  "FastAPI is required by the JD, but this skill was not found in your CV."

✗  "Since you already know FastAPI, you can skip this section."
✗  "You have experience with FastAPI, so learn Kubernetes next."
```

### 5.3 — `why` Must Acknowledge Missing Evidence

The `why` field must **always** acknowledge that evidence was not found:

```
✓  "{skill} evidence was not found in the parsed CV."
✓  "The JD requires {skill}, but no {skill} evidence was found in your CV."

✗  "You don't know {skill}."
✗  "You lack experience with {skill}."
```

### 5.4 — Priority Mapping

| Skill Type | Priority |
|---|---|
| `must_have` missing | `high` |
| `nice_to_have` missing | `medium` or `low` |
| Skills already matched | **No roadmap item** |

### 5.5 — `cv_evidence_to_add_after_learning` Must Be Future-Facing

The guidance for what to add to the CV after learning must:

```
✓  "After completing the project, add a truthful CV bullet describing the task, your role, tools used, and actual outcome."

✗  "You already know this, so just add it to your CV."
```

### 5.6 — No "Already Know" Statements

The system must **never** say or imply:

- "Since you already know X, learn Y"
- "You have X experience, so focus on Y"
- "Your X skills are strong, so the roadmap focuses on Y"

### 5.7 — `estimated_effort` is Required

Every roadmap item must include a human-readable `estimated_effort` field:

| Priority | Suggested Range |
|---|---|
| `high` | `2-4 weeks` or `1-2 months` |
| `medium` | `1-2 weeks` or `2-4 weeks` |
| `low` | `1 week` or less |

---

## 6. Before/After Comparison Guardrails

### 6.1 — Score Delta Not Sufficient

A score improvement alone is **not sufficient** to declare a CV revision successful. The comparison must evaluate:

- Evidence quality improvement
- Skill gap resolution
- Whether new evidence is real or keyword stuffing

### 6.2 — Resolved Skills Require Real Evidence

A skill moves to `resolved_missing_skills` only when:

- The base result had the skill as **missing**
- The revised result has the skill as **matched**
- There is **CV evidence** (project bullet, specific detail) supporting the match

Listing a skill without project evidence is **not** sufficient to resolve a gap.

### 6.3 — Keyword Stuffing Must Produce Warnings

When keyword stuffing is detected, the comparison **must** include `keyword_stuffing_warnings`. Keyword stuffing includes:

- Listing skills without supporting project evidence
- Repeating keywords without adding new context
- Adding irrelevant skills to inflate match count

### 6.4 — Improvement Summary Rules

The `improvement_summary` must:

- Acknowledge the score delta
- Reference evidence quality (not just the numeric score)
- Mention keyword stuffing warnings if present
- **NOT** say "all gaps resolved" unless all gaps are genuinely resolved with evidence

### 6.5 — Irrelevant Content Changes

When a CV revision adds content **not relevant** to the JD:

- The `improvement_summary` must note the irrelevance
- The score must **not** increase significantly from irrelevant additions
- `resolved_missing_skills` must **not** include skills unrelated to the JD

---

## 7. Keyword Stuffing Detection Rules

### 7.1 — Weak Keyword Detection

The keyword stuffing detector must flag skills that are:

- Listed in the skills section **without** project evidence
- Repeated in multiple bullets without adding new details
- **Not matched** with any meaningful CV evidence

### 7.2 — Severity Levels

| Pattern | Severity |
|---|---|
| 1-2 unsupported matches | `medium` |
| 3+ unsupported matches | `medium` (aggregate warning) |
| Repeated keyword spam | `high` |

### 7.3 — Warning Message Format

Every keyword stuffing warning must include:

```
{
  "skill": "{skill name}",
  "severity": "medium",
  "message": "The revised CV mentions {skill}, but project or responsibility evidence was not found. Add truthful context if you have it; otherwise keep it as a learning goal."
}
```

### 7.4 — Not Punishing Legitimate Improvements

Keyword stuffing detection must **not** flag:

- Real project evidence added with specific details
- Genuine skill additions with project context
- Metrics, outcomes, or architectural decisions added with real evidence

---

## 8. Privacy and Security Guardrails (Phase 1-4)

*(Carried forward from Phase 1, v1.5)*

### 8.1 — Sensitive Key Scrubbing

These keys must **never** appear in any output (API, report, logs):

```
access_token | access_token_hash | authorization | bearer | bucket
cv_text | file_path | jwt | local_path | object_key
password | password_hash | raw_cv_text | report_docx_path
s3_key | secret | storage_path | user_password
```

### 8.2 — URL Redaction

URLs containing `access_token` or other secrets must be redacted:

```
✓  https://api.example.com/v1/jobs/abc/result?access_token=<hidden>
✗  https://api.example.com/v1/jobs/abc/result?access_token=abc123secret
```

### 8.3 — Token Handling

- `access_token` must not appear in browser console
- `access_token` must not appear in logs
- JWT must not appear in `console.log`
- Error messages must not expose tokens or paths

---

## 9. Guardrail Violation Handling

### 9.1 — Blocker Violations (Must Fix Before Merge)

These patterns are **always blockers**:

```
"guarantee" + "hired" / "selected" / "interview" in same output
"you don't know" / "you don't have" + skill name
"you already know" + skill in learning roadmap
"since you know" + skill in learning roadmap why field
Invented years of experience
Invented company names
Invented metrics or numbers
do_not_fabricate: false
do_not_claim_until_completed: false
```

### 9.2 — High Severity (Must Fix Before Merge)

- Fabricated experience in improvement actions
- Finished rewrite claims with invented details
- Questions about skills not in CV or JD
- Score improvement from irrelevant content changes
- Keywords stuffed without warnings

### 9.3 — Medium Severity (Fix in Next Sprint)

- Missing `why_this_question` in interview prep
- Vague `risk_if_user_cannot_answer`
- Priority inflation (nice-to-have marked as `high`)

### 9.4 — Low Severity (Fix When Convenient)

- Minor wording issues in limitations
- Incomplete `estimated_effort` fields

---

## 10. Wording Reference Card

### DO SAY

```
"FastAPI evidence was not found in the parsed CV."
"JD requires FastAPI, but evidence was not found."
"If you have actually used FastAPI, add a truthful project bullet."
"Only add this if it is true."
"Fit score is an estimate and does not guarantee any hiring outcome."
"The JD mentions Kubernetes, but Kubernetes evidence was not found."
"After completing the Kubernetes project, add a truthful CV bullet."
"Missing evidence means support was not found in the parsed CV."
"The revised CV score improved by X points, but evidence quality still matters."
```

### NEVER SAY

```
"You don't know FastAPI."
"You have no PostgreSQL experience."
"You are guaranteed to be hired."
"Add 3 years of FastAPI experience."
"You worked at Google before."
"Since you already know FastAPI, learn Kubernetes."
"Your Python skills are strong."
"Built a FastAPI API serving 1M users." (fabricated)
"guarantee you will get the job"
"Since you know Python, FastAPI is easy to learn."
```

---

## 11. Phase 4 Specific Wording Rules

### Safe Rewrite Output

```
source_evidence: [bullet or evidence ID]
suggested_structure: Template with [brackets] for user to fill
warning: "Only use details that are true and can be defended in an interview."
missing_context_to_confirm: [list of facts user must verify]
do_not_fabricate: true
```

### Interview Prep Output

```
question: Specific question tied to CV evidence or JD gap
type: project_deep_dive | gap_probe | technical | behavioral | system_design
why_this_question: Non-empty, explains relevance
related_jd_requirement: Non-empty string
related_cv_evidence: Non-empty list for project_deep_dive, [] for gap_probe
suggested_answer_outline: Non-empty list of guidance bullets
risk_if_user_cannot_answer: Non-empty, meaningful risk description
```

### Learning Roadmap Output

```
skill: Non-empty skill name
priority: high | medium | low (high only for must-have missing)
why: Future-facing, mentions evidence not found in parsed CV
topics: Non-empty list of learning topics
mini_project: Specific, achievable project suggestion
estimated_effort: Non-empty effort estimate
cv_evidence_to_add_after_learning: Future-facing guidance
do_not_claim_until_completed: true
```

---

## 12. Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-05 | Initial guardrails (Phase 1/2) |
| 1.5 | 2026-06-05 | Added Phase 3 guardrails: missing skill wording, improvement actions, low-fit cap, evidence IDs, rewrite constraints |
| 2.0 | 2026-06-09 | Phase 4: Added safe rewrite, interview prep, learning roadmap, comparison, keyword stuffing, before/after guardrails |

---

*This document is the source of truth for AI CV Fit Phase 4 guardrails. Update before merging Phase 4 features that affect output wording.*
