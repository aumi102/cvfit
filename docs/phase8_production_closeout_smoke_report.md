# Phase 8 Production Closeout Smoke Report

**Environment:** Render production
**Evidence window:** 2026-07-22 15:58-17:23 UTC / 2026-07-22 22:58 to
2026-07-23 00:23 UTC+07
**Data classification:** Synthetic Phase 8 closeout account and the existing
`Demo Company` / `Demo Frontend Developer` fixture only; no real personal data
**Operator:** Codex with microphone consent and a short spoken synthetic answer
provided by the product owner

## Deployment Identity

| Service | Evidence | Result |
|---|---|---|
| Backend | `/health` and Render deployment metadata | `280cb96c0e6501cb42aa58eb5fae43c1e5022805`, production, healthy |
| Frontend | `/api/version` and Render deployment metadata | `280cb96c0e6501cb42aa58eb5fae43c1e5022805`, production, root HTTP 200 |
| Worker | Render background-worker deployment metadata | `280cb96c0e6501cb42aa58eb5fae43c1e5022805`, Live |
| PostgreSQL | backend Render Web Shell, `python scripts/run_alembic.py current` | `20260716_0001 (head)` |

The shared Render environment group contains the required realtime provider,
session-limit, throttle, frontend API-base, and CORS keys. Values and credentials
were not copied into this report. A production privacy-delete attempt exposed a
non-secret deployment mismatch: effective CORS methods initially omitted
`DELETE`. The operator changed only `CORS_ALLOWED_METHODS` to the repository
contract `GET,POST,DELETE,OPTIONS`, allowed the linked services to redeploy, and
then verified an OPTIONS preflight returned HTTP 200 with DELETE allowed.

## Browser and Device

- Browser: Codex in-app browser (Chromium-based; the controlled surface does
  not expose an exact browser version).
- Desktop viewport observed: 1274x714.
- Mobile responsive check: explicit 390x844 viewport, reset after the test.
- Host OS: Windows.
- Browser console evidence: no warning or error entries after text, voice,
  history, deletion, and mobile checks.
- No screenshot, recording, raw audio, token, Authorization header, full
  transcript, or private payload is retained.

## Results

| Flow | Result | Production evidence |
|---|---|---|
| Vietnamese text | PASS | New questions were Vietnamese; one short synthetic Vietnamese answer submitted; deterministic feedback, strengths, improvements, and recommendations rendered in Vietnamese; no console error. |
| Voice/WebRTC | PASS | No-recording notice and microphone consent were visible; WebRTC reached `Đã kết nối`; the live transcript distinguished `AI` and `Bạn`; AI prompts/transcript were Vietnamese; mute and unmute both worked; completion produced a Vietnamese summary. Audible output was experienced by the product-owner-operated microphone session but was not recorded. |
| Reconnect/throttle | PASS | DevTools Network Offline did not sever the existing WebRTC transport, so a bounded system WLAN disconnect/reconnect was used. UI moved through `Đã ngắt kết nối` and `Đang kết nối lại...`, displayed `Máy chủ yêu cầu chờ 3 giây trước khi kết nối lại.`, and returned to `Đã kết nối`. Backend endpoint/status evidence was client-secret `200 -> 409 -> 200`, with no 409 loop; transcript remained one AI entry, completion occurred exactly once, and the session was deleted exactly once. |
| History | PASS | `/history/[jobId]` opened the synthetic result, direct refresh preserved the detail, evidence controls were clickable, browser Back returned to History, desktop/mobile controls were visible, and backend logs showed OPTIONS 200 plus GET 200 for the synthetic report download. No freeze, overlay, redirect loop, or console error was observed. |
| Privacy deletion | PASS | Owner deletion succeeded after CORS reconciliation; an already-open second summary tab repeated DELETE successfully; direct summary became unavailable; a read-only DB query returned session/turn/event/summary counts `0/0/0/0` while the linked synthetic application remained `1`. Cross-owner behavior remains covered by automated production-module tests. |
| Retention dry-run | PASS | `python scripts/purge_realtime_interviews.py --retention-days 30 --batch-limit 500` reported dry-run mode, zero candidates, zero deleted, and printed no IDs/transcripts. No production purge executed. |

## Network Summary

- Text and history authenticated reads/submission completed without a failed
  request loop.
- Voice lifecycle event ingestion, completion, and summary requests completed
  successfully.
- The successful reconnect observation used a 9-second system WLAN interruption.
  The browser honored the backend throttle instead of repeatedly requesting a
  credential: initial issuance returned `200`, the early reconnect attempt
  returned one `409` with `Retry-After`, and the bounded retry returned `200`.
  The UI exposed a cancel action while waiting. No reconnect ran after explicit
  completion, no transcript entry duplicated, and summary/completion was not
  submitted twice.
- The first privacy preflight returned HTTP 400 because deployed CORS allowed
  only GET/POST/OPTIONS. After the minimal configuration correction and
  redeploy, the same DELETE preflight returned HTTP 200 and the UI deletion
  completed twice without disclosure.
- Backend logs were inspected only through endpoint/status summaries. They did
  not expose transcript content, credentials, tokens, or provider payloads.
- After the reconnect run, owner deletion returned `204`. A final read-only
  query found zero Phase 8 closeout synthetic realtime sessions and zero child
  session/turn/event/summary rows. Linked non-realtime synthetic fixture data
  was not deleted.

## Current Gate

This report is reproducible evidence for text, voice, reconnect/throttle,
history, mobile layout, privacy deletion, retention dry-run, deployed identity,
and console/network behavior. All synthetic realtime sessions created for the
closeout were removed. The explicit product-owner QA/privacy acceptance is
recorded in `phase8_team_closeout.md` and `phase8_privacy_review.md`.

**Production closeout smoke verdict:** PASS for the reviewed runtime SHA and
Maintenance/Portfolio Mode. This is not a claim that every browser/device has
been tested or that future deployments can skip their own bounded smoke.
