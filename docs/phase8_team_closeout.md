# Phase 8 Team Closeout — Authoritative Source of Truth

**Candidate date:** 2026-07-22  
**Authoritative repository:** `aumi102/cvfit`  
**Status:** closeout candidate; not complete until the replacement PR, review,
CI, deployment identity, and controlled production smoke gates below pass.

This document supersedes the Phase 8 status portions of the historical PR #99,
#100, #101, #102 implementation/handoff reports and the stale unmerged PR #98.
Those documents remain useful provenance, but this is the current team-level
gate.

## Scope and PR Reconciliation

| PR | State/role |
|---|---|
| #99 | merged backend foundation |
| #100 | merged initial frontend foundation; later superseded where mock-only |
| #101 | merged backend reconciliation/hardening |
| #102 | merged Vietnamese WebRTC voice and history recovery |
| #98 | stale/open replacement target; must not merge or cherry-pick |
| Replacement closeout PR | pending creation/CI/review/merge |

The replacement work salvages the intent of PR #98—multilingual evaluation,
malicious-flow QA, privacy review, browser evidence, and sign-off—but imports
the current production modules and canonical API. It does not retain conflict
markers, silent import skips, local stub models, `/start`, `/turns`, media
deletion, or `InterviewMediaArtifact` assumptions.

## Team Contributions

- **Phúc:** canonical backend/session lifecycle, migration, credential service,
  Unicode deterministic evaluator, throttle contract, deletion/retention, build
  identity, backend tests, and deployment architecture.
- **Quân:** visible text/voice modes, direct provider WebRTC with ephemeral
  credential, microphone/remote audio/transcript lifecycle, ordered event
  sequencer, bounded reconnect, summary UI, history detail recovery, and
  frontend tests.
- **Đạt/reviewer:** replacement QA fixtures/report and privacy/malicious-flow
  checklist are implemented here. Independent QA/privacy approval and team
  acceptance remain pending until recorded on the replacement PR and deployed
  smoke evidence.

## Architecture and API

The product uses a FastAPI API, Next.js primary frontend, Celery worker, Redis,
PostgreSQL, and private object storage. Browser audio connects directly to
OpenAI Realtime over WebRTC with a short-lived client credential issued by the
backend. The long-lived provider key never enters frontend code.

The seven canonical lifecycle routes remain:

1. `POST /v1/interview/realtime/sessions`
2. `GET /v1/interview/realtime/sessions`
3. `GET /v1/interview/realtime/sessions/{id}`
4. `POST /v1/interview/realtime/sessions/{id}/client-secret`
5. `POST /v1/interview/realtime/sessions/{id}/events`
6. `POST /v1/interview/realtime/sessions/{id}/complete`
7. `GET /v1/interview/realtime/sessions/{id}/summary`

The additive privacy route is
`DELETE /v1/interview/realtime/sessions/{id}`. JWT ownership is required;
cross-owner access is non-disclosing. The feature is fail-closed by default,
while deletion remains available when creation is disabled.

Client-secret throttle responses are `409` with an exposed integer
`Retry-After`. The browser uses a fresh ephemeral credential after bounded,
cancellable waiting and never reconnects after explicit completion.

## Database and Migration

The expected single Alembic head is `20260716_0001`. Phase 8 session, event,
turn, and summary tables already exist. Existing foreign keys/relationships
cascade children when a session is hard-deleted, so the closeout adds no
migration and performs no production migration in the implementation session.

## Security and Privacy

- Server owns model, voice, Vietnamese instructions, transcription language,
  tools policy, rubric, ownership, retention, and recording policy.
- Events start at zero, remain contiguous, allow exact replay, reject changed
  duplicate/gap/arbitrary payload, and store no SDP/audio/video/provider JSON.
- Transcript provenance is `client_reported_validated`; it is not provider
  cryptographic attestation.
- Credentials are memory-only and excluded from URL, storage, analytics, and
  logs.
- Realtime data has a 30-day maximum retention with owner hard delete and a
  dry-run-by-default bounded purge.
- No emotion, personality, honesty, protected-attribute, or hiring-probability
  inference is allowed.

See [phase8_privacy_review.md](phase8_privacy_review.md) and
[phase8_data_retention_and_deletion.md](phase8_data_retention_and_deletion.md).

## Evaluation and Browser QA

The production evaluator is `deterministic_transcript_v2_unicode`. The 21-case
synthetic Vietnamese/English/mixed set passes repeated determinism, bounds,
semantic, evidence, empty/adversarial, and output-language checks. It is a
bounded practice heuristic, not hiring validation.

Mock browser coverage includes history detail/interactions, mobile interview
layout, Vietnamese text practice, WebRTC transcript, 409 throttle wait,
reconnect, mute, one completion, summary, console checks, and resource cleanup.
See [phase8_rubric_evaluation_report.md](phase8_rubric_evaluation_report.md) and
[phase8_browser_device_qa_report.md](phase8_browser_device_qa_report.md).

## Build Identity and Deployment

- Backend: `GET /health` exposes only service, commit SHA, environment, and
  build time in addition to status.
- Frontend: `GET /api/version` exposes the same allowlisted identity.
- Worker: `python scripts/show_build_metadata.py --service worker` prints the
  allowlisted identity in its reviewed deployment shell/log.

`RENDER_GIT_COMMIT` is preferred. A health page that opens with
`commit_sha=unknown` is not deployed-SHA evidence. API/frontend/worker must use
the reviewed replacement merge SHA and the database must report the expected
head before production closeout.

## CI Gates

The replacement commit must pass Backend Checks, Frontend Checks, PostgreSQL
Migration Checks, production-module multilingual evaluation, unit/component
tests, Next build, and Playwright mock flows. PostgreSQL validation must run a
disposable upgrade/downgrade/upgrade cycle. Jobs may not call paid OpenAI,
payOS, production services, or require production secrets.

Local results may be recorded in the replacement PR, but GitHub Actions on the
final PR head is the remote source of truth. A pass on an older SHA is invalid.

## Production Smoke Gates

After merge and reviewed deployment, a synthetic account must prove:

- Vietnamese text question/answer/feedback.
- Voice consent, WebRTC connection, Vietnamese AI audio/transcript,
  mute/unmute, end, and summary.
- Safe disconnect/reconnect without a `409` loop or duplicate transcript/event.
- History detail, direct refresh, retry, report action, browser back, and no
  invisible overlay/console or failed-request loop.
- Owner deletion, idempotent repeat, cross-owner protection, and child cascade.

No real CV/transcript, recording, video, secret, or payment mutation is allowed.

## Dependency Risk

Targeted upgrades remove the critical Axios/form-data and moderate PostCSS
findings. The final `npm audit --omit=dev` reports two high package nodes
(`next` and transitive `sharp`) for the same `sharp/libvips` advisory chain.
The repository does not use `next/image`; npm offers only a semver-major Next
downgrade while `sharp` 0.35 is outside the Next 15 optional range. It is tracked separately
in [GitHub issue #103](https://github.com/aumi102/cvfit/issues/103) and must be
re-evaluated before introducing image processing.

## Rollback and Known Limitations

Disable realtime with `ENABLE_REALTIME_INTERVIEW=false`, then roll frontend,
backend, and worker back to recorded compatible SHAs. This closeout adds no
migration to downgrade. Stop the purge schedule separately.

Known limitations: browser-to-provider policy is not cryptographic
immutability; transcript text is client-reported; the rubric is lexical; live
provider/browser/device behavior still requires controlled evidence per deploy;
hard deletion may persist temporarily in infrastructure backups according to
the approved backup lifecycle.

## Sign-offs and Final Gate

| Gate | State |
|---|---|
| Implementation and local evidence | frontend lint (one documented warning), 28/28 unit tests, clean production build, and 4/4 Playwright flows pass with a clean runner exit; the previous backend run passed 705 tests with one PostgreSQL-only SQLite skip, but the final added PostgreSQL cascade test and strengthened evaluation gate await CI because this shell has no backend virtualenv and the local Docker daemon is unavailable |
| GitHub CI on final head | pending |
| Independent reviewer approval | pending |
| QA/privacy approval (Đạt or delegate) | pending |
| Replacement PR merged | pending |
| PR #98 superseded comment and closure | pending until replacement merge |
| Backend/frontend/worker SHA and DB head | pending |
| Controlled production synthetic smoke | pending |

**Closeout verdict:** NOT YET CLOSED. Phase 8 becomes complete only when every
row above is evidenced; this document must then be updated with exact PR, SHA,
CI run IDs, deployment metadata, smoke date/environment, and sign-offs.
