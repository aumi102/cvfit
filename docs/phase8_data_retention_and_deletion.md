# Phase 8 Realtime Retention and Deletion Runbook

The authoritative retention decision is
[phase8_privacy_review.md](phase8_privacy_review.md): realtime session metadata,
events, turns, and summary have a 30-day maximum retention and are hard-deleted
together.

## User-Initiated Deletion

Authenticated owners can delete from the summary screen or call:

```text
DELETE /v1/interview/realtime/sessions/{session_id}
```

The endpoint returns `204` for an owned, missing, already deleted, or
cross-owner ID. This deliberately avoids leaking whether another user's session
exists. The operation does not delete the application, target job, CV, account,
or other interview sessions.

## Operator Purge

**Owner:** Nguyễn Đức Hoàng Phúc, sole maintainer.
**Temporary schedule:** one manual operator check per local calendar day
(`Asia/Ho_Chi_Minh`) while production is online. There is no automated cron at
closeout. A fixed Render Cron Job may replace this process only after cost,
timezone, alerting, access, and disable behavior are reviewed.

From a reviewed backend deployment, first inspect a dry-run:

```bash
python scripts/purge_realtime_interviews.py --retention-days 30 --batch-limit 500
```

After backup policy, privacy approval, target environment, and schedule are
confirmed, execute one bounded batch:

```bash
python scripts/purge_realtime_interviews.py --retention-days 30 --batch-limit 500 --execute
```

Repeat only through an approved scheduled job. The script does not print
session IDs or transcript text. `--retention-days` cannot be less than 1 and
batch size is bounded to 500. It uses the existing application database
configuration and must never be pointed at production from an unapproved local
shell. The owner records date, environment, dry-run count, executed count, and
result without recording row IDs or transcript content.

## Verification

For a synthetic session, verify after deletion:

1. The owner GET returns the safe not-found response.
2. Session, event, turn, and summary rows no longer exist.
3. The linked application/job still exists.
4. Repeating DELETE returns `204`.
5. Another owner cannot use the ID to discover or delete the session.
6. Logs contain no transcript, credential, authorization header, or raw
   provider payload.

The production closeout performed the dry-run command with zero candidates and
zero deletions; no broad purge was executed. It also deleted each reconnect
smoke session through the owner endpoint. The final read-only query found zero
closeout synthetic realtime sessions and zero associated session/event/turn/
summary rows. Linked application fixture data remained intact.

## Rollback and Recovery

Hard deletion is intentionally irreversible at the application layer. Stop a
scheduled purge by disabling its operator schedule; do not attempt an Alembic
downgrade. Recovery, if legally and operationally appropriate, can only come
from an approved encrypted database backup and follows the infrastructure
backup-retention policy.
