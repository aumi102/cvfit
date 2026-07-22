# Phase 8 Repository Reconciliation

> Historical reconciliation baseline for PR #101. The canonical contract is
> retained, while completion/evaluation/privacy/deployment gates now live in
> `docs/phase8_team_closeout.md`.

**Date:** 2026-07-21

**Owner:** Phúc

**Scope:** Reconcile the merged Realtime AI Interview backend before completing
Phúc-owned backend, test, CI, migration, and documentation work.

**Status:** Canonical contract established; Phase 8 is not team-complete and is
not enabled for production users.

## Repository truth

The reconciliation starts from `main` at merge commit `21f99c2`, which contains
PR #99 (`a8aa974` plus the Alembic-head test correction `ec63d0b`). On
2026-07-21 the live GitHub `origin/main` ref resolved to the same commit.

The following local files are not part of Phase 8 work and must remain
untracked/uncommitted: `AGENTS.md`, `CLAUDE.md`, `.agents/skills/gitnexus/*`,
`.claude/skills/gitnexus/*`, `.claude/settings.local.json`, `.gitnexus/*`, and
`.env`.

## Canonical Phase 8 sources

The canonical source of truth is the merged implementation, in this order:

1. `backend/app/api/routes/interview_realtime.py` for the public HTTP surface.
2. `backend/app/schemas/interview_realtime.py` for accepted and returned JSON.
3. `backend/app/services/interview_realtime/` for lifecycle, ownership,
   provider configuration, event validation, transcript persistence, and
   summary behavior.
4. `backend/app/db/models.py` plus Alembic revision `20260716_0001` for the
   persisted model.
5. `backend/app/core/config.py` for fail-closed feature/provider settings.
6. `docs/interview_realtime_api_contract.md` and
   `docs/interview_realtime_backend_architecture.md`, after they are updated in
   this branch to match the completed backend work.

The implementation report records evidence and limitations; it does not
override code or the API contract.

## Canonical API and persistence

The supported API remains exactly these seven operations:

```text
POST /v1/interview/realtime/sessions
GET  /v1/interview/realtime/sessions
GET  /v1/interview/realtime/sessions/{session_id}
POST /v1/interview/realtime/sessions/{session_id}/client-secret
POST /v1/interview/realtime/sessions/{session_id}/events
POST /v1/interview/realtime/sessions/{session_id}/complete
GET  /v1/interview/realtime/sessions/{session_id}/summary
```

Persistence remains four media-free tables:

```text
interview_realtime_sessions
interview_realtime_turns
interview_realtime_events
interview_realtime_summaries
```

Target jobs and application workspaces both reuse owned `applications` rows.
The backend stores no raw audio, video, SDP, provider credential, or arbitrary
provider event object. Camera preview is frontend-local. There is no
`InterviewMediaArtifact` model or media-deletion API in the current MVP.

## Lifecycle and summary decisions

The canonical lifecycle is:

```text
setup -> ready -> active -> completed
  |       |         |
  +------>aborted<--+
  +------>failed<---+
```

Creation performs `setup -> ready`. Successful client-secret issuance performs
`ready -> active`. Completion is explicit and terminal. Repeating completion
must be idempotent and may retry a failed/pending server-side summary without
allowing the client to replace persisted turns or submit scores.

The canonical rubric dimensions are `relevance`, `specificity`, `evidence`,
`structure`, `technical_depth`, `communication_clarity`, and `risk`. The
summary is versioned, server-generated practice feedback. It is not a hiring
decision and does not infer emotion, personality, honesty, truthfulness,
protected attributes, or hiring probability.

## Trust and provider-control decision

Browser-reported transcript and provider lifecycle metadata are not
cryptographically trusted. They are accepted only as client-reported data after
strict event-type, field, scalar-type, size, ordering, idempotency, ownership,
and lifecycle validation. Server-owned values include the user/session owner,
context ownership, lifecycle, timestamps written by the server, feature flags,
model policy, instructions, tool policy, rubric version, scores, and summary
status.

The browser cannot submit user IDs, scores, rubric outcomes, model names,
instructions, tools, provider configuration, retention rules, recording policy,
or arbitrary provider JSON to the CVFit API.

OpenAI's current client-secret reference states that attached session
configuration can be overridden by the client connection. Therefore the
ephemeral-token architecture cannot make provider session configuration
cryptographically immutable. This branch will keep the agreed direct-browser
WebRTC architecture and mitigate the limitation by:

- building the complete provider configuration from server settings, owned
  context, versioned instructions, and validated session preferences;
- exposing no provider-configuration request body on the client-secret route;
- forbidding protected `session.update` overrides in Quân's contract;
- treating all browser-relayed transcripts/events as client-reported;
- generating scores and summaries only on the backend; and
- keeping the feature disabled until browser QA confirms the frontend does not
  issue protected overrides.

Moving to the OpenAI unified `/v1/realtime/calls` interface could put session
configuration under stronger server control, but it would place SDP through the
backend and change the approved architecture. That is not introduced silently
in this completion branch.

## Conflicting cached branch artifacts

`origin/DLIGHT_Phase8_Finish` is based on `7e0c8fd`, before PR #99. It must not
be merged or cherry-picked as a whole.

Do not reuse its backend tests because they:

- define test-local replacement models instead of importing production models;
- silently return when the current route cannot be imported;
- expect obsolete `/start` and `/turns` endpoints;
- expect a different feature flag and status-code behavior;
- expect an `InterviewMediaArtifact` table and media-delete route; and
- can pass when the implementation under test is absent.

The branch's QA/privacy checklist ideas and evaluation-case concepts may be
salvaged by Đạt only after being rewritten against the canonical seven-route,
four-table contract. The evaluation corpus and quality conclusions remain
Đạt's scope and are not claimed by this backend branch.

`origin/phase7/frontend-ui-ux-improvements` is unrelated Phase 7 frontend work
and must be rebased/reviewed separately by Quân. `origin/DLIGHT-phase7-`
contains older status documentation and must not override main's current
implementation or this Phase 8 contract.

## Stale status claims

- `README.md`, `docs/database_migrations.md`, and older Render documents still
  describe pre-Next.js, pre-auth, or old Alembic-head states and require scoped
  correction.
- Phase 5 and Phase 6 closeout documents still contain incomplete team sign-off
  claims; this branch will not rewrite those phases or declare them complete.
- Phase 7 remains payment-credential blocked and its billing/credit flags remain
  off. Phase 8 does not change that decision.
- The PR #99 implementation report accurately labels its work as a foundation,
  but must be updated with the completion branch's actual tests, migration
  evidence, and remaining frontend/QA/privacy/live-smoke blockers.

## Team handoff decision

Quân must integrate only the canonical seven endpoints and strict schemas
documented in `docs/interview_realtime_api_contract.md`. He must not create
compatibility calls to `/start`, `/turns`, or media APIs and must not send
protected `session.update` overrides. Camera preview remains local and the
ephemeral client secret remains memory-only.

Đạt must test the production models/routes/services directly, with a mocked
provider and no silent import skips. His QA/evaluation must recognize the
client-reported transcript trust boundary, versioned server-side rubric,
pending/ready/failed summary flow, strict event sequence/idempotency contract,
no-media policy, and protected-override limitation.

Branch disposition:

- PR #99 code on `main`: retain and harden.
- `origin/DLIGHT_Phase8_Finish`: selectively salvage human-reviewed QA ideas;
  discard its backend contract and tests.
- Quân's later frontend work: rebase onto the completed backend branch and use
  the canonical handoff contract.
- Đạt's later QA/evaluation work: start from the completed backend branch and
  rewrite tests/fixtures against production code.

Completing Phúc's scope does not mean `PHASE8_COMPLETE`, team completion,
production readiness, or live Realtime verification.
