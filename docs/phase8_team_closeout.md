# Phase 8 Team Closeout — Authoritative Source of Truth

**Closeout date:** 2026-07-23
**Authoritative repository:** `aumi102/cvfit`  
**Status:** runtime, QA, privacy, deployment, and production-smoke gates pass.
This document becomes the final repository record when its closeout PR passes
review/CI and merges without a protection bypass.

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
| #98 | closed unmerged on 2026-07-22; superseded because its contract/tests were stale and CI was red |
| #104 | merged replacement closeout on 2026-07-22; approved and green; merge SHA `280cb96c0e6501cb42aa58eb5fae43c1e5022805` |

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
- **Đạt/reviewer scope:** PR #98 was not merged. Its useful QA intent was
  rewritten against production modules in PR #104: multilingual fixtures,
  malicious-flow coverage, privacy/retention decisions, browser evidence, and
  evaluation reports. No new approval or signature is attributed to Đạt.

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
`commit_sha=unknown` is not deployed-SHA evidence. The controlled closeout
verified backend, frontend, and worker at
`280cb96c0e6501cb42aa58eb5fae43c1e5022805`, and PostgreSQL at
`20260716_0001 (head)`. Provider and feature configuration were checked only as
masked/presence evidence; no secret value was copied.

## CI Gates

PR #104 passed CI run
[`29912736873`](https://github.com/aumi102/cvfit/actions/runs/29912736873)
on its merge SHA: Frontend Checks job `88899292028`, Backend Checks job
`88899292044`, and PostgreSQL Migration Checks job `88899292043` all succeeded.
That run covered production-module multilingual evaluation, unit/component
tests, Next build, Playwright mock flows, and the disposable PostgreSQL
upgrade/downgrade/upgrade cycle. The final documentation PR must independently
pass all configured checks on its own head. CI calls neither paid OpenAI nor
payOS, uses no production secret, and performs no deployment.

## Production Smoke Gates

The controlled synthetic account proved:

- Vietnamese text question/answer/feedback.
- Voice consent, WebRTC connection, Vietnamese AI audio/transcript,
  mute/unmute, end, and summary.
- Safe disconnect/reconnect without a `409` loop or duplicate transcript/event.
- History detail, direct refresh, retry, report action, browser back, and no
  invisible overlay/console or failed-request loop.
- Owner deletion, idempotent repeat, and child cascade; cross-owner protection
  is covered by production-module automated tests rather than a second live user.

The reconnect run used an actual bounded WLAN interruption because DevTools
Network Offline did not sever the already-established WebRTC transport. UI
transitioned through disconnected/reconnecting, displayed the server-requested
3-second wait, and returned to connected. Backend endpoint/status evidence was
one `200 -> 409 -> 200` client-secret sequence, not a loop, followed by exactly
one completion and one deletion. Transcript state did not duplicate. A final
read-only database query found zero remaining closeout synthetic realtime
sessions and zero session/turn/event/summary rows for the deleted run.

No real CV/transcript, recording, video, secret, or payment mutation was used.
See [phase8_production_closeout_smoke_report.md](phase8_production_closeout_smoke_report.md).

## Dependency Risk

Targeted upgrades remove the critical Axios/form-data and moderate PostCSS
findings. The final `npm audit --omit=dev` reports two high package nodes
(`next` and transitive `sharp`) for the same `sharp/libvips` advisory chain.
The repository does not use `next/image`; npm offers only a semver-major Next
downgrade while `sharp` 0.35 is outside the Next 15 optional range. It is tracked separately
in [GitHub issue #103](https://github.com/aumi102/cvfit/issues/103) as a
non-blocking accepted maintenance risk and must be re-evaluated before
introducing image processing.

## Rollback and Known Limitations

Disable realtime with `ENABLE_REALTIME_INTERVIEW=false`, then roll frontend,
backend, and worker back to recorded compatible SHAs. This closeout adds no
migration to downgrade. Stop the purge schedule separately.

Known limitations: browser-to-provider policy is not cryptographic
immutability; transcript text is client-reported; the rubric is lexical; a
desktop Chromium-based production smoke does not represent every physical
device/browser; and hard-deleted rows may persist temporarily in infrastructure
backups according to the provider lifecycle.

## Sign-offs and Final Gate

| Gate | State |
|---|---|
| Implementation and local evidence | PASS: frontend lint (one documented warning), 28/28 unit tests, clean production build, 4/4 Playwright flows with clean exit; backend and PostgreSQL coverage confirmed by CI |
| Replacement PR #104 | PASS: approved, CI green, merged as `280cb96c0e6501cb42aa58eb5fae43c1e5022805` |
| PR #98 disposition | PASS: superseded comment recorded and PR closed unmerged |
| Backend/frontend/worker SHA and DB head | PASS: all services at `280cb96c0e6501cb42aa58eb5fae43c1e5022805`; DB `20260716_0001` |
| Controlled production synthetic smoke | PASS: Vietnamese text, voice, reconnect/throttle, history, mobile viewport, deletion/cascade, retention dry-run, and clean console/network checks |
| Privacy/operations | PASS for owner-operated Maintenance/Portfolio Mode: 30-day maximum, owner delete, daily manual purge ownership, no raw media/SDP, no sensitive inference |
| Final closeout documentation PR | must pass review, CI, and merge without bypass; GitHub metadata is the authoritative evidence |

## Product-owner acceptance

> Tôi, Nguyễn Đức Hoàng Phúc, với vai trò project owner và sole maintainer của AI CV Fit sau Phase 8, xác nhận đã xem xét kết quả CI, production deployment, synthetic smoke, QA và privacy controls. Tôi chấp nhận Phase 8 cho mục đích vận hành ở Maintenance/Portfolio Mode, với retention tối đa 30 ngày, owner-scoped deletion, không lưu raw audio/video/SDP và không thực hiện sensitive inference. Xác nhận này không phải chứng nhận pháp lý và không đại diện cho chữ ký mới của các thành viên cũ.

**Closeout decision:** all runtime and operational gates are evidenced for
Maintenance/Portfolio Mode. This decision becomes the final repository
closeout when the documentation PR containing it is reviewed, green, and
merged. Maintenance ownership, purge cadence, cost control, rollback, archive,
and risk review are defined in [maintenance_mode.md](maintenance_mode.md).
