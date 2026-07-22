# Phase 8 Realtime Interview — Frontend Handoff for Quân

> Status: implemented on the Phase 8 closeout replacement branch. This file is
> now the maintenance contract; `docs/phase8_team_closeout.md` owns final gates.

**Contract version:** 1.1

**Backend configuration version:** `realtime_session_vi_v2`

**Status:** frontend integration implemented; replacement CI/review and
current-SHA controlled live evidence remain approval gates

Use only the authenticated API below. The backend flag is disabled by default,
so `503` is normal until an operator deliberately enables a non-production
environment.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/interview/realtime/sessions` | Create an owned ready session |
| `GET` | `/v1/interview/realtime/sessions?limit=20&offset=0` | List owned sessions |
| `GET` | `/v1/interview/realtime/sessions/{id}` | Read owned session and turns |
| `POST` | `/v1/interview/realtime/sessions/{id}/client-secret` | Mint in-memory ephemeral credential |
| `POST` | `/v1/interview/realtime/sessions/{id}/events` | Submit one validated client event |
| `POST` | `/v1/interview/realtime/sessions/{id}/complete` | Finalize turns idempotently |
| `GET` | `/v1/interview/realtime/sessions/{id}/summary` | Poll practice summary |

All endpoints require the existing JWT Bearer token. A missing resource and a
cross-owner resource both return `404`.

## Allowed session-create fields

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

- Interview type: `technical`, `behavioral`, `project_deep_dive`, `hr`, `mixed`.
- Difficulty: `easy`, `medium`, `hard`.
- Mode: `realtime_voice` or `audio_fallback`.
- `question_limit` is `1..20` and may be lower at runtime.
- Linked IDs must belong to the signed-in user. `target_job_id` and
  `application_id`, when both present, must be equal.
- Realtime voice requires `consent_audio=true`.
- Camera is local preview metadata only. Never upload camera frames.
- Recording must remain `false`; the backend rejects `true` and stores no media.
- Unknown request fields are rejected.

## Forbidden overrides

Do not send arbitrary OpenAI/provider JSON to CV Fit or in a later
`session.update`. The frontend must not override model, provider, voice, system
instruction, hidden prompt, tools, tool choice, generation controls, maximum
duration, recording/retention policy, rubric/evaluator version, owner, linked
resource ownership, entitlement, or internal metadata.

The client-secret response returns `model`, `voice`, and
`configuration_version` for display/debug comparison only. They are not
frontend choices. Official OpenAI behavior allows the browser to update most
session fields; this contract forbids doing so. The backend does not claim that
direct WebRTC makes those settings cryptographically immutable.

## Browser flow and state

1. Collect explicit microphone consent and create the session.
2. Expect `ready`.
3. Request a client secret; keep `client_secret` in memory only and use it
   immediately. Never log it, persist it, put it in analytics, or include it in
   an event.
4. Connect browser-to-OpenAI with WebRTC. CV Fit does not proxy SDP/audio/video.
5. Send allowlisted events with a local sequence starting at `0` and increment
   by exactly one after each accepted event.
6. Complete with the final bounded turns. Repeating the same completion after a
   lost response is safe and does not duplicate turns.
7. Poll summary. Treat `202/pending`, `200/ready`, and `200/failed` as explicit
   UI states.
8. Stop local media tracks and disconnect at the configured time/question
   limit. Do not assume the server can close the direct peer connection.

On reconnect, close the old peer/data channel/audio element but reuse the one
consented live microphone stream. Mint a fresh ephemeral credential. A
client-secret throttle returns `409` plus `Retry-After`; wait that duration,
retry at most three times, expose a cancel action, and stop all retry work after
the user ends or the component unmounts. A microphone track with
`readyState=ended` requires new consent and must not trigger another secret
request.

Persisted states are `setup`, `ready`, `active`, `completed`, `aborted`, and
`failed`. The public happy path is `ready -> active -> completed`. Do not invent
`/start`, `/turns`, or media-delete calls.

## Event contract

Allowed event types:

- `session_connected`
- `session_disconnected`
- `question_started`
- `question_completed`
- `user_transcript_completed`
- `assistant_transcript_completed`
- `session_error`

Send only the flat fields documented in
`docs/interview_realtime_api_contract.md`; never forward raw provider events.
Unknown/nested/sensitive/media-like/oversized data returns `422`. An exact retry
of the same sequence, type, and validated payload returns `201` with
`replayed=true`. Reusing a sequence with different content or skipping a
sequence returns `409`; resynchronize from the last locally acknowledged event
instead of changing old payloads.

Transcript and provider item IDs are client-reported but validated. They are
not provider-attested and must not be presented as verified evidence.

## Completion and summary

Completion accepts only `turn_index`, `question_text`, bounded `question_type`,
`answer_transcript`, optional `ai_followup_text`, and timestamps plus the
bounded completion reason. Never submit score, feedback, rubric, provider
event, key, or instruction fields.

Summary dimensions are `relevance`, `specificity`, `evidence`, `structure`,
`technical_depth`, `communication_clarity`, and `risk`. Each ready dimension is
an object with `score`, `max_score`, and `evidence_turn_ids`. Always show the
practice-only disclaimer and limitations. Do not translate the score into a
hiring probability.

## Errors the UI must handle

| Status | UI behavior |
|---|---|
| `401` | Re-authenticate through the existing auth flow |
| `404` | Treat session/context as unavailable; do not reveal ownership details |
| `409` | Show lifecycle/throttle/order conflict; retry only when safe |
| `422` | Show bounded consent/input validation feedback |
| `503` | Feature/provider unavailable; keep the rest of the app usable |

Do not display provider response bodies; the backend intentionally returns
sanitized messages.

## Local/mock integration

Frontend work can proceed without OpenAI credentials by mocking the seven HTTP
routes with the exact schemas above and using a fake in-memory client-secret
value that never leaves the mock boundary. Simulate:

- feature-disabled `503`;
- ready/active/completed session responses;
- exact event replay and sequence conflict;
- client-secret throttle `409`;
- throttle `Retry-After`, cancel/end during the wait, offline/online, revoked
  microphone, and unexpected data-channel close;
- summary `202/pending`, `200/ready`, and `200/failed`;
- microphone denial and recording rejection.
Do not call paid APIs or add a real key to frontend environment variables.
