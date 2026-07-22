# Phase 8 Realtime Interview — QA/Evaluation Handoff for Đạt

> Status: superseded as a pending checklist by the executable production-module
> fixtures/tests and reports linked from `docs/phase8_team_closeout.md`. PR #98
> was closed unmerged after replacement PR #104 was reviewed, green, and merged.

**Rubric version:** `realtime_practice_v1`

**Evaluator version:** `deterministic_transcript_v2_unicode`

**Transcript provenance:** `client_reported_validated`

**Status:** replacement evaluation, malicious-flow review, privacy decision,
browser QA, reviewer approval, and controlled deployed smoke are recorded

This handoff defines the independent evaluation boundary. Passing automated
tests is evidence of contract behavior; it is not a claim of hiring validity or
live-provider verification. The executable dataset and measured result are in
`backend/tests/fixtures/phase8_rubric_evaluation.json` and
`docs/phase8_rubric_evaluation_report.md`.

## Trust model

Server-trusted data: authenticated owner, linked-resource ownership, lifecycle,
server timestamps, feature/provider configuration, safe server lifecycle
events, rubric/evaluator version, summary status, and server-generated scores.

Client-reported but validated data: transcript/question text, bounded speaker
semantics implied by allowlisted event type, provider item ID, browser
timestamp, connection/error metadata, completion reason, and consent choices.

Not client-controlled: user ID, entitlement, application ownership, provider
key/model/instruction/tools, retention/recording policy, rubric version,
evaluator provenance, dimension scores, overall score, or hiring outcome.

Direct WebRTC provides no provider signature for submitted transcript events.
Tests and reports must not label them cryptographically verified. This data may
support low-stakes practice feedback only.

## Rubric schema

Ready summaries expose these dimensions:

```text
relevance
specificity
evidence
structure
technical_depth
communication_clarity
risk
```

Each dimension contains a `0..5` score, `max_score=5.0`, and
`evidence_turn_ids`. `overall_score` is bounded `0..100`. Stored rubric metadata
also contains `status`, `rubric_version`, `evaluator_version`, and transcript
provenance. Public summaries can be `pending`, `ready`, or `failed`; a failed
summary uses `summary_generation_failed` and retains its turns for retry.

The evaluator is a deterministic text heuristic. It must never be evaluated as
an emotion, personality, deception, protected-attribute, or hiring-prediction
model.

## Existing fixtures and fakes

- `backend/tests/test_interview_realtime.py` exercises production schemas,
  routes, session service, provider builder, and evaluator through in-memory DB
  fakes and FastAPI dependency overrides.
- Provider HTTP is mocked; tests must not call OpenAI or require a paid key.
- `backend/tests/test_interview_realtime_postgres.py` inspects the disposable
  PostgreSQL Phase 8 schema after the CI migration cycle.
- `backend/tests/test_phase8_env_contract.py` validates disabled-by-default,
  provider configuration, billing isolation, and secret-safe output.

Do not copy the local stub models or import-and-return behavior from
`origin/DLIGHT_Phase8_Finish`. Its useful human scenarios should be rewritten
against the current seven routes and four models.

## Required QA cases

### Contract/security

- Missing/invalid JWT and all cross-user session/context paths.
- Attempts to submit owner, score, rubric, evaluator, model, instruction, tools,
  provider JSON, retention, and recording overrides.
- Unknown event type/field; nested payload; oversized payload/text; base64-like
  media; token/key/SDP/audio/video field names; credential-like values.
- Event start at a nonzero sequence, gaps, conflicting duplicate, and exact
  idempotent replay.
- Client-secret ownership, terminal state, expired session, repeated issuance
  inside the interval, provider timeout, malformed provider response, and
  missing configuration.
- Repeated completion, duplicate turn indexes, excessive turns, reversed
  timestamps, and summary failure/retry without turn loss.

### Privacy/product

- Confirm no server key/ephemeral credential/provider body appears in API
  responses, persisted event metadata, normal logs, or test snapshots.
- Confirm raw audio, video, SDP, and raw provider payload are never accepted or
  stored; confirm recording consent is rejected.
- Confirm camera preview stays browser-local.
- Confirm learning tasks are proposals only and no roadmap mutation occurs.
- Confirm no billing, credit, or payOS path is invoked.
- Confirm every summary displays practice-only limitations and contains no
  emotion/personality/truthfulness/protected-attribute/hiring-probability field.

### Rubric quality

Create synthetic, privacy-safe transcript fixtures for empty/minimal, concise
relevant, evidence-rich STAR, technically deep, irrelevant, unsupported
absolute-claim, Vietnamese, English, and mixed-language answers. Review:

- determinism and bounded scores;
- monotonic behavior for added relevant evidence;
- evidence-turn traceability;
- risk-dimension behavior without calling the user dishonest;
- missing-answer behavior;
- language bias and false confidence;
- usefulness and non-discrimination of recommendations;
- stable rubric/evaluator versioning.

The replacement evaluation thresholds and results are recorded in
`docs/phase8_rubric_evaluation_report.md`; do not tune the heuristic silently
inside QA artifacts.

## Browser/live blockers

Browser WebRTC behavior, microphone permissions, reconnection, live transcripts,
accessibility, and provider session-update behavior are not satisfied by backend
unit tests alone. Automated regressions and the bounded production evidence are
recorded separately in `docs/phase8_browser_device_qa_report.md` and
`docs/phase8_production_closeout_smoke_report.md`; future runtime changes must
repeat the relevant gates.
