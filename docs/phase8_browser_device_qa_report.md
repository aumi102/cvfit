# Phase 8 Browser and Device QA Report

**Local automated environment:** Windows, Microsoft Edge `150.0.4078.83`
through Playwright  
**Run date:** 2026-07-22  
**Data:** synthetic identities and mocked backend/provider only

## Reproducible Automated Matrix

| Scenario | Evidence | Expected gate |
|---|---|---|
| Chromium/Edge desktop history detail | `phase8-hotfix.spec.js` | direct detail, clickable actions, no console errors |
| Mobile 375x812 interview layout | `phase8-hotfix.spec.js` | voice/text tabs usable, no horizontal overflow |
| Vietnamese text practice | `phase8-hotfix.spec.js` | `language=vi`, submit and Vietnamese feedback |
| Voice/WebRTC mock | `phase8-hotfix.spec.js` | consent, remote transcript, mute, complete, summary |
| 409 reconnect throttle | browser + unit tests | honor `Retry-After`, no request loop, one completion |
| Permission denied/revoked | component/unit tests | readable error, no orphan stream |
| Offline then online | client unit tests | bounded reconnect only after online |
| Unexpected data-channel close | client unit tests | reconnect state, cleanup |
| Summary pending/ready/failed | component tests | explicit state and retry behavior |
| Feature disabled/provider unavailable | component/API tests | Vietnamese fallback message, text mode remains usable |
| History timeout/error/retry | history tests | loading clears and actions remain reachable |
| Expired JWT/cross-owner | backend tests | auth state or safe not-found; no disclosure |

The repository runner starts `next start` as an owned child process, launches
Playwright only after a bounded readiness probe, and tears down that exact
process tree on every exit path. This avoids the Windows open-handle failure
observed when Playwright directly owned the Next.js web server. Browser context,
reconnect timers, peer connection, data channel, audio element, and microphone
mock are also closed on teardown. A valid run must exit with code 0 after the
tests pass; a printed pass count followed by a hanging process is a failure of
this gate.

The recorded local run completed all four flows and exited normally:

```text
4 passed (15.2s)
process exit code: 0
```

The final `npm run test:e2e` command returned in 17.8 seconds on the local
Windows runner. A one-flow History reproduction also returned code 0 in 8.3
seconds, proving the exit behavior is not hidden by the voice test teardown.

The deliberately mocked `409` client-secret throttle is the only console
network error allowlisted in the reconnect flow; it is handled and followed by
a successful retry. No page errors or other console errors were observed. A
separate read-only in-app browser check loaded the Vietnamese landing page with
title `AI CV Fit Analyzer — Phân tích CV thông minh` and an empty error log.

## Malicious-Flow Review

- Sequence gap and changed duplicate events are rejected; exact replay is
  idempotent.
- Client event payloads cannot include SDP, media, provider keys, raw provider
  JSON, score, rubric, owner, or arbitrary instructions.
- Prompt injection and fake JSON remain transcript text and cannot replace the
  server-owned evaluator/configuration.
- Cross-owner reads and mutation are non-disclosing.
- Reconnect is bounded and cancellable; user completion prevents later retry.
- Credentials remain in function scope and are absent from storage, URL,
  analytics, and logs.

## Manual and Production Evidence

The product owner reported that voice worked on the day before this audit. That
is useful supplementary evidence, but the browser version, exact timestamp,
deployed SHA, synthetic account, network trace, and console result were not
provided and are not invented here.

Required controlled production rows remain pending until recorded against the
replacement merge SHA:

| Browser/device | Scenario | State |
|---|---|---|
| Current Chromium desktop | Vietnamese text, voice, mute/end/summary | pending |
| Current Chromium desktop | disconnect/reconnect without 409 loop | pending |
| Current Chromium desktop | history refresh/retry/download | pending |
| Mobile viewport/device | interview modes and history actions | pending |
| Browser with microphone denied then allowed | consent and recovery | pending |

No screenshot or video is included yet. Any later artifact must use only a
synthetic account and must not contain a credential, real CV, private
transcript, raw audio, or video recording.
