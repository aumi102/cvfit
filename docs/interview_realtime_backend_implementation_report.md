# Realtime Interview Backend Implementation Report — Phase 8

**Owner:** Phúc
**Date:** 2026-07-16
**Branch:** `phase8/phuc-realtime-interview-backend`
**Scope:** Backend foundation only; frontend and QA/evaluation work remain separate

## Scope completed

- Added owner-scoped realtime interview session, turn, minimized event, and
  summary persistence.
- Added explicit lifecycle transitions and terminal-state protection.
- Added ownership validation for linked target jobs, applications, and analysis
  jobs, including owned fallback to `best_analysis_job_id`.
- Added minimal context construction and fixed server-side interviewer
  instructions.
- Added the current OpenAI Realtime client-secret REST flow with a short-lived
  credential, fixed timeouts, pseudonymous safety identifier, and safe provider
  errors.
- Added fail-closed feature/configuration behavior.
- Added strict event allowlists, payload minimization, credential/media
  rejection, and payload hashing.
- Added bounded final-turn persistence and deterministic seven-dimension rubric
  aggregation when trusted backend scores exist.
- Added stable API and backend architecture documentation.

No frontend, billing/payment, evaluation, automated test, media-storage, or
learning-task creation work is included.

## Files changed

### Backend configuration and registration

- `.env.example`
- `backend/app/core/config.py`
- `backend/app/db/init_db.py`
- `backend/app/main.py`

### Backend models, schemas, routes, and services

- `backend/app/db/models.py`
- `backend/app/schemas/interview_realtime.py`
- `backend/app/api/routes/interview_realtime.py`
- `backend/app/services/interview_realtime/__init__.py`
- `backend/app/services/interview_realtime/errors.py`
- `backend/app/services/interview_realtime/context_builder.py`
- `backend/app/services/interview_realtime/instruction_builder.py`
- `backend/app/services/interview_realtime/realtime_client_service.py`
- `backend/app/services/interview_realtime/event_redaction.py`
- `backend/app/services/interview_realtime/session_service.py`
- `backend/app/services/interview_realtime/summary_service.py`

### Alembic and Phúc-owned documentation

- `backend/alembic/versions/20260716_0001_add_realtime_interview_tables.py`
- `docs/interview_realtime_api_contract.md`
- `docs/interview_realtime_backend_architecture.md`
- `docs/interview_realtime_backend_implementation_report.md`

## Database changes

Revision `20260716_0001` follows `20260623_0001` and preserves one Alembic
head. It creates:

- `interview_realtime_sessions`
- `interview_realtime_turns`
- `interview_realtime_events`
- `interview_realtime_summaries`

Foreign keys link sessions to the owning user and optional existing
application/target-job and analysis records. Child rows use `ON DELETE
CASCADE`. Indexes cover session ownership, context links, status, creation
time, event type, and child session IDs. Unique constraints cover turn index per
session, optional event sequence per session, and one summary per session. The
downgrade drops only these Phase 8 objects in dependency-safe order.

The runtime expected head is advanced to `20260716_0001`.

## Endpoints implemented

- `POST /v1/interview/realtime/sessions`
- `GET /v1/interview/realtime/sessions`
- `GET /v1/interview/realtime/sessions/{session_id}`
- `POST /v1/interview/realtime/sessions/{session_id}/client-secret`
- `POST /v1/interview/realtime/sessions/{session_id}/events`
- `POST /v1/interview/realtime/sessions/{session_id}/complete`
- `GET /v1/interview/realtime/sessions/{session_id}/summary`

The detailed schemas, status codes, allowed events, lifecycle, and frontend
expectations are defined in `docs/interview_realtime_api_contract.md`.

## Feature flags and deployment configuration

```env
ENABLE_REALTIME_INTERVIEW=false
OPENAI_API_KEY=
OPENAI_REALTIME_MODEL=
OPENAI_REALTIME_VOICE=
OPENAI_REALTIME_SESSION_MAX_MINUTES=15
OPENAI_REALTIME_MAX_QUESTIONS=5
```

The feature is disabled by default. All Phase 8 routes return `503` while it is
disabled. Missing API key, model, or voice returns `503` from client-secret
issuance; no fake credential is produced. Provider configuration is checked at
request time, so a disabled deployment starts safely. Payment/payOS settings
are not consulted.

Deployment must apply reviewed migration `20260716_0001` through the existing
operator-controlled migration workflow before enabling the flag. The runtime
also needs outbound HTTPS access to `api.openai.com`. No migration was run
against a production database.

## Provider integration status

The backend uses the current official direct HTTP contract:

```text
POST https://api.openai.com/v1/realtime/client_secrets
```

It sends the backend API key only in the provider Authorization header and
returns only the short-lived provider value and expiration metadata to the
authenticated owner. The credential is never stored or logged. A mocked
provider-contract smoke check passed. A live provider call was intentionally
not made because no real credential/model/voice configuration was supplied.

## Summary and rubric status

The persisted contract supports `overall_score`, the seven approved rubric
dimensions, strengths, weaknesses, suggested improvements, next practice
questions, proposed learning tasks, and limitations.

The deterministic aggregator runs only when every completed turn already has a
complete trusted backend `score_json`. The frontend cannot submit scores. No
trusted AI evaluator populates those scores in this implementation, so normal
completion safely returns summary `pending` rather than fabricated feedback.

## Validation results

- `python -m compileall backend/app`: passed using a temporary pycache path
  because pre-existing workspace cache files are locked.
- Ruff check over changed backend Python: passed.
- Backend model/service ownership and persistence smoke: passed, including
  cross-user rejection and deterministic score aggregation (`74`).
- OpenAPI smoke: passed; all seven operations across six new paths are present,
  and the existing typed interview route remains registered.
- Provider contract/fail-closed smoke: passed.
- `python scripts/ci_guard.py`: passed.
- `alembic heads`: one head, `20260716_0001`.
- `alembic history`: unbroken `20260623_0001 -> 20260716_0001` chain.
- Alembic offline PostgreSQL SQL generation through head: passed.
- Existing migration metadata tests: `27 passed`.
- Existing backend suite excluding four files that cannot collect without the
  locally missing `python-docx`: `581 passed, 10 failed`. The remaining failures
  are eight auth tests without a working bcrypt backend, one storage test with
  locally missing Celery, and one test-owned hard-coded assertion for the old
  Alembic head. No test files were changed under the ownership boundary.
- Disposable PostgreSQL upgrade: not run because Docker Desktop is not running;
  this remains a deployment validation step before enabling the feature.

Final diff, ownership, secret, and GitNexus affected-scope checks are recorded
at commit handoff.

## Dependencies for Quân

Quân can integrate against the seven documented routes and strict schemas. His
later frontend must manage the browser WebRTC connection, explicit microphone
permission UI, in-memory use of the ephemeral credential, event mapping to the
seven allowed metadata types, explicit completion, pending-summary handling,
and browser disconnect at the configured limits. The browser must not override
instructions/model/tools or send raw provider events, SDP, media, credentials,
or Authorization data.

## Dependencies for Đạt

Đạt should later test authentication and non-leaking ownership, linked-context
ownership, audio consent, disabled/misconfigured `503` behavior, provider error
safety, event/type/field/size redaction, credential and media rejection,
duplicate sequences, lifecycle transitions, completion bounds, and
pending/ready summaries. This implementation does not add or modify tests, QA
checklists, privacy reviews, evaluation reports, compatibility reports, E2E
reports, or closeout documents.

## Remaining backend work

- Implement or connect a trusted backend transcript/rubric evaluator that
  populates turn scores; until then, summary pending is the intended contract.
- Validate upgrade/current/downgrade/re-upgrade against disposable pgvector
  PostgreSQL before deployment; Docker was unavailable locally.
- Reconcile the existing test-owned hard-coded Alembic-head assertion in Đạt's
  later test work.
- Decide whether immutable provider session configuration requires a future
  server-side-control architecture; the ephemeral-token protocol permits the
  client connection to override session configuration, and the current browser
  contract forbids such overrides.
