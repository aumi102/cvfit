# Realtime Interview API Contract — Phase 8

**Version:** 1.1
**Date:** 2026-07-21
**Backend owner:** Phúc
**Status:** Backend contract implemented; frontend and QA remain separate work

## Scope and base contract

The Phase 8 API is an authenticated, owner-scoped backend contract for a
browser WebRTC interview using a short-lived OpenAI Realtime client secret.

- Base path: `/v1/interview/realtime`
- Authentication: JWT Bearer via the existing `get_current_user` dependency
- Cross-user lookup: `404` to avoid revealing resource existence
- Content type: `application/json`, except the browser's later direct WebRTC
  exchange with OpenAI, which is outside this backend route contract
- Feature flag: every route returns `503` while
  `ENABLE_REALTIME_INTERVIEW=false`
- Billing: no payment, payOS, or credit rule is applied to these routes

The backend accepts only bounded interview options. It does not accept a system
prompt, model instruction, tool definition, API key, SDP, audio, or video.

## Session lifecycle

Persisted statuses are:

```text
setup -> ready -> active -> completed
  |       |         |
  +------>aborted<--+
  +------>failed<---+
```

Allowed transitions:

| From | To |
|---|---|
| `setup` | `ready`, `aborted`, `failed` |
| `ready` | `active`, `completed`, `aborted`, `failed` |
| `active` | `completed`, `aborted`, `failed` |
| `completed` | none |
| `aborted` | none |
| `failed` | none |

Creation validates ownership and moves the internal `setup` row to `ready` in
one transaction. Successful client-secret issuance moves `ready` to `active`.
Completion accepts `ready` or `active` and moves it to `completed`. Invalid or
terminal transitions return `409`.

## Shared request values

### Mode

```text
realtime_voice
audio_fallback
```

### Interview type

```text
technical
behavioral
project_deep_dive
hr
mixed
```

### Difficulty

```text
easy
medium
hard
```

Unknown mode, type, or difficulty values return FastAPI/Pydantic `422`.

## Session schemas

### `RealtimeInterviewSessionCreate`

```json
{
  "target_job_id": null,
  "application_id": null,
  "analysis_job_id": null,
  "interview_type": "mixed",
  "difficulty": "medium",
  "question_limit": 5,
  "mode": "realtime_voice",
  "consent_audio": true,
  "consent_camera": false,
  "consent_recording": false
}
```

Rules:

- All context IDs are optional UUIDs.
- Every supplied ID must belong to the authenticated user.
- Target jobs reuse the existing `applications` table. If both
  `target_job_id` and `application_id` are supplied, they must be equal.
- An omitted `analysis_job_id` is resolved from the linked application's
  `best_analysis_job_id` when available and ownership is rechecked.
- `question_limit` is `1..20` at schema level and must not exceed
  `OPENAI_REALTIME_MAX_QUESTIONS` at runtime.
- `consent_audio=true` is mandatory for `realtime_voice`.
- Camera consent is optional. No camera data is sent to this backend.
- Recording consent must remain `false`; `true` is rejected because this
  backend has no media recorder, media table, or deletion route.
- Extra request fields are forbidden.

### `RealtimeInterviewSessionResponse`

```json
{
  "id": "uuid",
  "target_job_id": null,
  "application_id": null,
  "analysis_job_id": null,
  "mode": "realtime_voice",
  "status": "ready",
  "interview_type": "mixed",
  "difficulty": "medium",
  "question_limit": 5,
  "consent_audio": true,
  "consent_camera": false,
  "consent_recording": false,
  "started_at": null,
  "ended_at": null,
  "failure_code": null,
  "created_at": "2026-07-16T10:00:00",
  "updated_at": "2026-07-16T10:00:00",
  "turn_count": 0,
  "turns": []
}
```

List responses leave `turns` empty but report `turn_count`. A single-session
read includes ordered, bounded turn records. Neither response contains events,
provider payloads, secrets, SDP, or media.

### `RealtimeInterviewSessionListResponse`

```json
{
  "items": [],
  "total": 0,
  "limit": 20,
  "offset": 0
}
```

`limit` is `1..100`; `offset` is non-negative. Only the current user's sessions
are counted and returned.

## Endpoints

### `POST /v1/interview/realtime/sessions`

- Auth: required
- Body: `RealtimeInterviewSessionCreate`
- Response: `201 RealtimeInterviewSessionResponse`
- Validates context ownership, consent, configured question limit, and bounded
  options before persisting a `ready` session.
- Errors: `401`, `404`, `422`, `503`

### `GET /v1/interview/realtime/sessions`

- Auth: required
- Query: `limit=20`, `offset=0`
- Response: `200 RealtimeInterviewSessionListResponse`
- Errors: `401`, `422`, `503`

### `GET /v1/interview/realtime/sessions/{session_id}`

- Auth: required owner
- Response: `200 RealtimeInterviewSessionResponse`
- Errors: `401`, `404`, `503`

### `POST /v1/interview/realtime/sessions/{session_id}/client-secret`

- Auth: required owner
- Body: none
- Requires `consent_audio=true` and status `ready` or `active`
- Requires the Phase 8 flag, server API key, realtime model, and voice
- Rejects terminal sessions and active sessions beyond the configured maximum
- Builds context and system instructions on the backend
- Mints a short-lived OpenAI Realtime client secret using the server-owned TTL
- Enforces a persisted, per-session minimum issuance interval
- Does not persist or log the client secret
- Does not return the server `OPENAI_API_KEY`

Response schema `RealtimeClientSecretResponse`:

```json
{
  "interview_session_id": "uuid",
  "client_secret": "ephemeral-provider-value",
  "expires_at": 1784186460,
  "provider_session_id": "sess_provider_id-or-null",
  "model": "operator-configured-model",
  "voice": "operator-configured-voice",
  "configuration_version": "realtime_session_v1"
}
```

The frontend must keep `client_secret` in memory only, use it immediately for
the direct WebRTC connection, and never write it to logs, storage, analytics,
URL parameters, or backend events.

Errors:

- `401`: missing/invalid JWT
- `404`: missing/cross-user session or linked context
- `409`: invalid/terminal status or session time limit exceeded
- `409`: also returned when another secret was issued inside the configured
  minimum interval
- `422`: audio consent missing
- `503`: flag off, provider configuration missing, timeout, provider failure,
  or invalid provider response

### `POST /v1/interview/realtime/sessions/{session_id}/events`

- Auth: required owner
- Status: `201`
- Session must be `ready` or `active`
- Unknown event types, unknown payload fields, nested payloads, binary values,
  sensitive field names, credential-like strings, encoded media, and payloads
  above 16 KiB are rejected
- `event_sequence` is required, begins at `0`, and must increase by exactly one
  for each accepted client event
- Replaying the same sequence, event type, and validated payload hash is
  idempotent (`201`, `replayed=true`); reusing a sequence with different
  content or creating a gap returns `409`

Request schema `RealtimeEventCreate`:

```json
{
  "event_type": "question_started",
  "event_sequence": 3,
  "payload": {
    "turn_index": 0,
    "question_text": "Tell me about a relevant backend project.",
    "question_type": "project_deep_dive",
    "occurred_at": "2026-07-16T10:01:00Z"
  }
}
```

Allowed event types and flat payload fields:

| Event type | Allowed payload fields |
|---|---|
| `session_connected` | `provider_session_id`, `transport` (`webrtc`), `occurred_at` |
| `session_disconnected` | `reason`, `code`, `occurred_at` |
| `question_started` | `turn_index`, `question_text`, `question_type`, `occurred_at` |
| `question_completed` | `turn_index`, `question_text`, `question_type`, `occurred_at` |
| `user_transcript_completed` | `turn_index`, `transcript`, `provider_item_id`, `occurred_at` |
| `assistant_transcript_completed` | `turn_index`, `transcript`, `transcript_kind` (`question` or `followup`), `question_type`, `provider_item_id`, `occurred_at` |
| `session_error` | `code`, `message`, `retryable`, `occurred_at` |

`turn_index` must be within the session's configured question limit. Question
text is limited to 4,000 characters, transcript text to 12,000, follow-up text
to 4,000, and error messages to 500.

Question/transcript text is persisted in the owned turn table. The event table
stores only minimized metadata such as turn index, text length, provider item
ID, safe error fields, a SHA-256 hash of the validated payload, and timestamp.
It does not duplicate transcript or question text into the event payload.

Sensitive key concepts rejected at any payload key include:

```text
authorization
api_key
client_secret
token
sdp
audio
video
raw_media
```

Response:

```json
{
  "event_id": "uuid",
  "interview_session_id": "uuid",
  "event_type": "question_started",
  "event_sequence": 3,
  "accepted": true,
  "replayed": false,
  "created_at": "2026-07-16T10:01:00"
}
```

### `POST /v1/interview/realtime/sessions/{session_id}/complete`

- Auth: required owner
- Accepts `ready` or `active`; repeating completion after `completed` is
  idempotent and does not duplicate or replace turns
- Persists/upserts at most `question_limit` unique final turns
- Does not accept frontend scores, feedback, instructions, media, or provider
  secrets
- Validates text size, credential-like content, encoded media, turn indexes,
  unique indexes, and timestamp order
- Moves the session to `completed`
- Runs the bounded server-side deterministic practice evaluator over validated
  turns when at least one turn exists. Client-provided scores are not accepted
  or trusted.

`RealtimeSessionCompleteRequest`:

```json
{
  "turns": [
    {
      "turn_index": 0,
      "question_text": "Tell me about a relevant backend project.",
      "question_type": "project_deep_dive",
      "answer_transcript": "I built ...",
      "ai_followup_text": null,
      "started_at": "2026-07-16T10:01:00Z",
      "ended_at": "2026-07-16T10:02:30Z"
    }
  ],
  "completion_reason": "completed"
}
```

`completion_reason` is one of `completed`, `user_ended`, or `time_limit`. It is
accepted as bounded client metadata and is not used to bypass status rules.

Response:

```json
{
  "interview_session_id": "uuid",
  "status": "completed",
  "completed_turns": 1,
  "summary_status": "ready",
  "ended_at": "2026-07-16T10:02:30"
}
```

Errors: `401`, `404`, `409`, `422`, `503`.

### `GET /v1/interview/realtime/sessions/{session_id}/summary`

- Auth: required owner
- Returns `200` with `status=ready` or `status=failed` when a summary row exists
- Returns `202` with the same schema and `status=pending` when no summary row
  exists yet
- Never returns provider events, instructions, credentials, SDP, or media

`RealtimeInterviewSummaryResponse`:

```json
{
  "interview_session_id": "uuid",
  "status": "ready",
  "rubric_version": "realtime_practice_v1",
  "overall_score": 74,
  "rubric": {
    "relevance": {
      "score": 4.0,
      "max_score": 5.0,
      "evidence_turn_ids": ["turn-uuid"]
    }
  },
  "strengths": [],
  "weaknesses": [],
  "suggested_improvements": [],
  "next_practice_questions": [],
  "learning_tasks_to_create": [],
  "limitations": [],
  "failure_code": null,
  "disclaimer": "AI interview feedback is for practice only and does not predict hiring outcomes.",
  "created_at": "2026-07-16T10:03:00",
  "updated_at": "2026-07-16T10:03:00"
}
```

The only rubric dimensions are:

```text
relevance
specificity
evidence
structure
technical_depth
communication_clarity
risk
```

No emotion, face-derived confidence, personality, truthfulness, or hiring
probability fields exist.

The evaluator and rubric are server-owned. Transcript provenance is
`client_reported_validated`, not provider-attested; the score is a bounded
practice heuristic, not a hiring decision. A safe evaluation failure retains
turns and returns `status=failed` plus `failure_code=summary_generation_failed`
so a repeated completion request can retry.

## Ownership and consent rules

- The authenticated user must own the session and every linked application,
  target job, and analysis job.
- Cross-user access uses `404`, including linked-resource integrity failures.
- Session list/count queries always filter by `user_id`.
- Turn, event, and summary ownership is inherited through the owned parent
  session.
- `consent_audio=true` is required for realtime voice creation and for every
  client-secret request.
- `consent_camera` is metadata only. This backend never receives video.
- `consent_recording=false` is the default. This backend never records media.

## Error response contract

Expected domain errors use the existing FastAPI shape:

```json
{
  "detail": "human-readable safe message"
}
```

| Status | Meaning |
|---|---|
| `401` | JWT missing/invalid |
| `404` | Resource missing or not owned |
| `409` | Invalid lifecycle transition, issuance throttle, sequence conflict/gap |
| `422` | Schema, consent, bound, redaction, or safe-persistence validation failed |
| `503` | Feature disabled or provider unavailable/misconfigured |

FastAPI validation failures retain the normal structured `detail` array.
Provider response bodies and authorization details are never copied into error
responses.

## Frontend integration expectations for Quân

Quân may integrate against only the routes and schemas above. In particular:

1. Create an owned session and wait for `status=ready`.
2. Request a client secret only after explicit microphone consent.
3. Hold the returned ephemeral value in memory and immediately use it for the
   OpenAI WebRTC connection.
4. Do not send or override system instructions, model, voice, tools, or safety
   configuration from the browser.
5. Submit only the allowlisted, flat event payloads above. Never submit raw
   provider event objects.
6. Send assistant questions with `transcript_kind=question` before transcript-
   only events for a new turn.
7. Complete explicitly, then treat summary `202/pending` as a normal state.
8. Stop/disconnect the browser session at the configured question/time limit.

The official Realtime client-secret contract permits the browser to send a
later `session.update` for most session fields. The backend therefore cannot
cryptographically make the direct-WebRTC session configuration immutable. The
frontend contract forbids model, instruction, tool, voice, duration, retention,
recording, rubric, and provider overrides. The backend never accepts arbitrary
provider JSON and never treats browser transcript events as provider-attested.
Changing that trust property would require a separately reviewed provider
control/proxy architecture.

Frontend implementation, WebRTC code, permissions UI, transcript UI, and
analytics are not part of this backend contract implementation.
