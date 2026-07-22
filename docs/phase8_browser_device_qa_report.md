# Phase 8 Browser and Device QA Report

**Local automated environment:** Windows, Microsoft Edge `150.0.4078.83`
through Playwright  
**Run date:** 2026-07-22 to 2026-07-23
**Data:** synthetic identities; mocked provider for automation and a controlled
synthetic account for production smoke

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

The controlled production smoke ran against backend, frontend, and worker SHA
`280cb96c0e6501cb42aa58eb5fae43c1e5022805` on Render. The browser was the
Codex in-app Chromium-based surface on Windows; that controlled surface did not
expose an exact Chromium version, so none is invented. Desktop viewport was
1274x714 and the responsive production pass used 390x844. Automated Playwright
used Microsoft Edge `150.0.4078.83` and a 375x812 mobile viewport.

| Browser/device | Scenario | State/evidence |
|---|---|---|
| Production Chromium desktop | Vietnamese text, voice, mute/unmute, end, summary | PASS; Vietnamese question/feedback/audio transcript and summary rendered; no retained recording |
| Production Chromium desktop | disconnect/reconnect with throttle | PASS; actual system WLAN interruption, one `409` with server-requested 3-second wait, then reconnect; no loop, duplicate transcript, or double completion |
| Production Chromium desktop | history refresh/back/report | PASS; stable detail route, direct refresh, clickable evidence/report controls, successful report GET, no overlay or redirect loop |
| Production Chromium mobile viewport 390x844 | interview modes and history actions | PASS; core controls remained visible/clickable with no blocking layer |
| Automated Chromium/Edge | microphone denied/revoked, offline/online, cancel/end during wait | PASS; component/client regressions cover readable errors, bounded retry, and cleanup |

Chrome DevTools Network Offline alone did not transition the already-established
peer connection within the observation window. It is therefore recorded as a
tool limitation, not a pass. The final reconnect gate used a bounded 9-second
system WLAN interruption and observed `Đã ngắt kết nối`,
`Đang kết nối lại...`, a visible cancel action, the 3-second throttle message,
and `Đã kết nối`. Backend status evidence was client-secret
`200 -> 409 -> 200`, followed by exactly one completion and one owner deletion.
The final DB check found no closeout synthetic realtime session or child rows.

No page error or unexpected console warning/error was observed in the final
text, voice, reconnect, history, mobile, or deletion checks. The expected
handled `409` was visible only as endpoint/status evidence. No screenshot,
video, raw audio, Authorization header, credential, full transcript, or private
payload is retained. See
[phase8_production_closeout_smoke_report.md](phase8_production_closeout_smoke_report.md).
