# Realtime Interview Backend Architecture — Phase 8

**Date:** 2026-07-16
**Owner:** Phúc
**Scope:** Backend architecture, persistence, provider integration, contracts,
configuration, and deployment readiness only

## Architecture summary

Phase 8 adds a separate realtime-interview subsystem alongside the existing
Phase 5 typed-answer and Phase 6 Interview Practice v2 features. Existing
interview tables and routes remain unchanged.

```text
authenticated browser
        |
        | JWT + bounded JSON
        v
FastAPI /v1/interview/realtime
        |
        +--> ownership/session service --> PostgreSQL Phase 8 tables
        |
        +--> owned context builder --> server instruction builder
        |                                  |
        |                                  v
        +--> realtime client service --> OpenAI client-secrets REST API
                                               |
                                               v
                                short-lived client secret
                                               |
                                               v
                           browser WebRTC direct to OpenAI
```

The server API key stays on the backend. SDP and media stay between the browser
and OpenAI; this backend never accepts or persists them.

## Backend components

| Component | Responsibility |
|---|---|
| `app/api/routes/interview_realtime.py` | Seven authenticated endpoints and HTTP/domain error mapping |
| `app/schemas/interview_realtime.py` | Strict request/response types, bounded enums, consent and completion validation |
| `app/services/interview_realtime/session_service.py` | Ownership, persistence, pagination, transitions, event/turn writes, completion |
| `context_builder.py` | Minimal owned target-job/application/analysis/profile context |
| `instruction_builder.py` | Server-owned interviewer rules and prompt-injection boundary |
| `realtime_client_service.py` | Direct HTTP client-secret request with timeout and safe errors |
| `event_redaction.py` | Event and field allowlists, size limits, credential/media rejection, minimization, hashing |
| `summary_service.py` | Deterministic seven-dimension aggregation when trusted scores exist |
| `app/db/models.py` | Four additive SQLAlchemy models |
| Alembic `20260716_0001` | Four additive tables and single-head migration |

No Celery pipeline is introduced. Completion and deterministic aggregation are
synchronous and bounded. A future evaluator can use the existing worker pattern
if model-based rubric generation becomes necessary.

## OpenAI Realtime server-side flow

The implementation follows the current official ephemeral-token flow:

1. The authenticated browser requests the app's client-secret endpoint.
2. The backend rechecks session/context ownership, consent, lifecycle, time
   bound, feature flag, and provider configuration.
3. The backend builds minimal owned context and fixed interviewer instructions.
4. `httpx` sends `POST https://api.openai.com/v1/realtime/client_secrets` with
   the server API key and a SHA-256 pseudonymous `OpenAI-Safety-Identifier`.
5. The provider response is parsed into only the ephemeral value, expiration,
   provider session ID, configured model, and voice.
6. The ephemeral value is returned once, never persisted or logged.
7. The browser later establishes WebRTC directly with OpenAI.

Official reference:

- [OpenAI Realtime WebRTC guide](https://developers.openai.com/api/docs/guides/realtime-webrtc)
- [Create Realtime client secret API](https://developers.openai.com/api/reference/resources/realtime/subresources/client_secrets/methods/create)

The backend request configures:

- operator-selected realtime model and voice
- backend-generated instructions
- audio output
- near-field input noise reduction
- `gpt-4o-mini-transcribe` input transcription
- server VAD with bounded timing
- maximum 512 output tokens per response
- no tools and `tool_choice=none`
- 60-second client-secret creation TTL

The 60-second TTL limits when a new provider session may be created; it is not
the interview duration. The configured interview duration is enforced in
instructions and by rejecting reconnect/client-secret requests after the
backend active-session window. Quân's browser must also disconnect at the time
limit.

The provider API documents that client-secret session configuration may be
overridden by the client connection. This backend never accepts frontend
instructions and Quân's integration must not send instruction/model/tool
overrides. Cryptographic enforcement of immutable instructions would require a
future server-proxied/unified-interface or server-side-control design.

## Database design

### `interview_realtime_sessions`

Owns the lifecycle, user/context links, bounded options, explicit consent, and
failure/timing metadata. It does not contain provider secrets or media.

Foreign keys:

- `user_id -> users.id`
- `target_job_id -> applications.id` (nullable; target jobs reuse applications)
- `application_id -> applications.id` (nullable)
- `analysis_job_id -> analysis_jobs.id` (nullable)

Indexes cover ownership, context links, status, and creation time.

### `interview_realtime_turns`

Stores one logical question/answer turn per `(session_id, turn_index)`. The
unique constraint prevents duplicate turn identity. Text is bounded at API
ingestion. Optional score/feedback JSON is reserved for trusted backend
evaluation, not accepted from the frontend.

### `interview_realtime_events`

Stores an allowlisted event type, optional per-session unique sequence,
minimized metadata, SHA-256 payload hash, and creation time. It never stores raw
provider payloads, question/transcript text copies, headers, credentials, SDP,
or media.

### `interview_realtime_summaries`

One row per session via a unique session index. Stores overall score, rubric,
strengths, weaknesses, improvement recommendations, next practice questions,
proposed learning tasks, limitations, and timestamps.

Child tables use `ON DELETE CASCADE` at the database layer, although this PR
does not expose a session-delete route.

## Context-building flow

Context is rebuilt at client-secret issuance so ownership and current evidence
are revalidated immediately before the provider call.

1. Load only IDs explicitly linked to the session.
2. Require each application/target job/analysis row to match `user_id`.
3. Resolve an omitted analysis from an owned linked application's
   `best_analysis_job_id`.
4. Extract title, company, target role, status/readiness, and a bounded
   deterministic JD requirements summary.
5. From a succeeded analysis, extract only fit score, bounded score breakdown,
   matched/missing skills, bounded CV evidence snippets, readiness counts, and
   limitations.
6. Include at most eight owned career-profile items that intersect the role or
   analysis terms. Exclude profile source URLs and raw evidence fields.
7. Serialize the bounded structure below fixed instructions as explicitly
   untrusted reference data.

The builder does not read unrelated users, JWTs, access tokens, access-token
hashes, storage locations, report paths, raw full CV text, or raw full provider
data.

## Instruction safety

The server instruction builder fixes these rules:

- one question at a time
- configured type, difficulty, question count, and target duration
- job/evidence relevance
- no protected-attribute or sensitive-personal questions
- no emotion, face, personality, truthfulness, or hiring-probability inference
- no hiring guarantees
- uncertainty and missing evidence remain explicit
- no fabricated experience or metrics
- follow-ups must relate to the preceding answer
- clean termination after the final question

All context text is labeled untrusted data. The public API contains no
instruction field.

## Event redaction and transcript persistence

The route first validates a seven-value event-type allowlist and a per-event
flat field allowlist. It then:

1. Canonicalizes JSON and rejects payloads above 16 KiB.
2. Rejects nested structures and binary values.
3. Rejects sensitive key concepts (`authorization`, `api_key`,
   `client_secret`, `token`, `sdp`, `audio`, `video`, `raw_media`).
4. Rejects credential-like strings and long base64-like media.
5. Validates turn bounds, field lengths, choices, booleans, and timestamps.
6. Hashes the validated full payload with SHA-256.
7. Writes question/transcript content only to the owned turn table.
8. Writes only safe metadata and content lengths to the event table.

This is structural allowlisting, not string replacement.

## Summary and rubric foundation

The supported dimensions are:

```text
relevance
specificity
evidence
structure
technical_depth
communication_clarity
risk
```

When every completed turn contains a trusted backend score for every dimension,
the service deterministically averages dimensions, combines positive dimensions
with inverse risk into a 0–100 overall score, and creates bounded templated
recommendations. If any trusted score is missing, it persists turns, creates no
fake evaluation, and returns summary `202/pending`.

The frontend cannot submit score or feedback fields. Emotion, face-derived
confidence, personality, truthfulness, and hiring probability are excluded.

## Failure behavior

| Failure | Behavior |
|---|---|
| Feature flag off | All Phase 8 routes return `503`; startup remains healthy |
| API key/model/voice missing | Client-secret route returns `503`; no fake credential |
| Provider timeout/HTTP/invalid JSON | Safe `503`; provider body and auth are not returned |
| Cross-user ID | `404` non-leak response |
| Missing consent | `422` |
| Invalid/terminal status | `409` |
| Oversized/sensitive event | `422`, nothing persisted |
| Duplicate event sequence | `409` |
| Missing trusted rubric | Turns complete; summary remains `202/pending` |

Provider exceptions are converted to fixed messages. The server API key and
ephemeral value are never interpolated into exceptions.

## Deployment configuration

Required Phase 8 variables:

```env
ENABLE_REALTIME_INTERVIEW=false
OPENAI_API_KEY=
OPENAI_REALTIME_MODEL=
OPENAI_REALTIME_VOICE=
OPENAI_REALTIME_SESSION_MAX_MINUTES=15
OPENAI_REALTIME_MAX_QUESTIONS=5
```

Rules:

- Keep the flag `false` until the reviewed migration is applied and all three
  provider values are set in the backend secret environment.
- Never put a real key in `.env.example`, source control, logs, frontend config,
  or client responses.
- Session minutes must be `1..60`; maximum questions must be `1..20`.
- Missing provider configuration does not block app startup and does not affect
  payment/payOS routes. It fails closed only at the Phase 8 contract.
- Apply Alembic `20260716_0001` through the established backup/review/operator
  process. Do not run it automatically at application startup.
- API egress must allow HTTPS to `api.openai.com`; request timeout is 10 seconds
  with a 5-second connect timeout.
- WebRTC browser/network compatibility and TURN/ICE behavior are Quân/Đạt
  integration concerns, not modified here.

## Dependencies and handoff

### Quân

Quân can consume the stable contract in
`docs/interview_realtime_api_contract.md`. Remaining frontend work includes the
browser WebRTC connection, microphone/camera consent UI, media cleanup,
transcript/event mapping, pending-summary state, and client-side time/question
disconnect behavior. None is implemented here.

### Đạt

Đạt should later verify authentication/non-leak ownership, context ownership,
consent, disabled/misconfigured `503`, provider error safety, event allowlists,
payload bounds, credential/media rejection, duplicate sequences, lifecycle
conflicts, completion bounds, and pending/ready summary states. No tests, QA
documents, evaluation reports, privacy review, or closeout report are created
here.

## Known backend limitations

- A trusted transcript evaluator does not yet populate turn `score_json`; the
  deterministic aggregator is ready but normal completion therefore returns
  summary pending.
- Backend time limits prevent new/reconnect credentials after expiry but cannot
  forcibly close a direct browser-to-provider peer connection.
- Provider session settings can be client-overridden under the ephemeral-token
  protocol; the app contract forbids overrides, while immutable enforcement is
  future server-side-control work.
- No usage/billing enforcement or automatic learning-task creation is included.
