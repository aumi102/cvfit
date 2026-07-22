# Phase 8 Multilingual Rubric Evaluation Report

**Status:** replacement evidence for the stale PR #98 evaluator work  
**Evaluation date:** 2026-07-22  
**Evaluator:** `deterministic_transcript_v2_unicode`  
**Rubric:** `realtime_practice_v1`

## Scope and Method

The evaluation runs the production deterministic evaluator in
`app.services.interview_realtime.summary_service`; it does not use a stub model,
paid provider, production secret, or real user transcript. The source fixture is
`backend/tests/fixtures/phase8_rubric_evaluation.json` and the reproducible gate
is:

```bash
python scripts/evaluate_phase8_rubric.py --check
```

Each of 21 synthetic cases is evaluated five times. The runner checks stable
output, score bounds, required semantic expectations, and a Vietnamese output
contract. Unit tests separately check stable evidence turn IDs and the persisted
summary provenance.

## Dataset

- Languages: Vietnamese, English, and mixed Vietnamese/English.
- Domains: frontend, backend, data/AI, teamwork, problem solving, career
  motivation, project experience, and security.
- Quality: action plus quantified result, descriptive but missing result,
  generic, irrelevant, very short, empty, repeated question, and unsupported
  claims.
- Adversarial/edge: prompt injection, fake JSON, markup, emoji, decomposed
  Unicode, technical terms, near-limit long input, duplicate events, sequence
  gaps, and cross-owner access (the final three are API tests rather than rubric
  fixtures).

No fixture contains a transcript from a real user.

## Thresholds and Results

| Metric | Threshold | Result |
|---|---:|---:|
| Fixtures completed | 21 | 21 |
| Deterministic output | 100% | 100% |
| Score bounds (`0..5`, overall `0..100`) | 100% | 100% |
| Semantic expectations | 100% | 100% |
| Required Vietnamese output contract | 100% | 100% |
| Unsupported claim increases risk | required | pass |
| Empty answer remains safe | required | pass |
| Mixed-language stability | required | pass |

There were no hidden skips and no failed fixtures in the recorded 21-case local
run. The final runner additionally enforces Vietnamese recommendation prefixes;
that exact final revision awaits the replacement PR CI because the current
shell has no backend dependency environment. The CI workflow runs the same
command and is the authoritative remote gate for the replacement PR.

## Findings

- NFC normalization keeps Vietnamese diacritics intact, including decomposed
  input after normalization.
- Technical spellings such as `React.js`, `Next.js`, `C++`, `C#`, `.NET`, and
  `CI/CD` remain meaningful tokens.
- Action/result/structure matching accepts both English and Vietnamese phrases.
- A number inside fake JSON is not treated as a quantified result without
  result context.
- Evidence references use persisted turn IDs and are stable across repeated
  generation.
- Feedback and recommendations are actionable practice suggestions in
  Vietnamese; they do not claim hiring validity.

## Bias and Usefulness Review

The evaluator uses transcript text only. It does not inspect or infer emotion,
personality, honesty, employability, gender, age, ethnicity, disability, or
another protected/sensitive attribute. The rubric dimensions concern answer
relevance, specificity, evidence, structure, technical depth, communication
clarity, and unsupported-claim risk. Prompt-injection text cannot replace the
server-owned rubric or award a maximum score.

Manual inspection found the weakest-dimension recommendations understandable
and actionable for practice. This is a product-quality review, not validation
of predictive hiring accuracy or demographic fairness.

## Limitations and Verdict

The heuristic is lexical and cannot verify that a candidate's statement is
true. Browser transcripts are client-reported and validated by bounds, not
cryptographically provider-attested. English answers intentionally receive
Vietnamese summary UI because the product language is Vietnamese.

**Evaluation verdict:** PASS for the deterministic multilingual practice
contract. Independent PR review and deployed synthetic smoke remain separate
Phase 8 closeout gates.
