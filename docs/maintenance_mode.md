# AI CV Fit v1.0 Maintenance Mode

## Ownership

**Sole maintainer:** Nguyễn Đức Hoàng Phúc (`aumi102`)
**Role:** project owner, production operator, privacy/retention operator, and
incident contact after Phase 8.

Former team-member approvals remain historical pull-request evidence. This
policy does not claim new signatures, availability, or approval from former
team members and does not imply 24/7 support.

## Project Status

- Product: AI CV Fit v1.0.
- Mode: Maintenance / Portfolio Mode.
- Active feature development is paused.
- No Phase 9 is required or planned.
- Phase 8 runtime services were verified at
  `280cb96c0e6501cb42aa58eb5fae43c1e5022805`; PostgreSQL was verified at
  `20260716_0001 (head)`.

## Allowed Maintenance

- Critical security fixes and directly reachable dependency remediation.
- Production outage and data/privacy incident response.
- Required, scoped dependency upgrades with regression evidence.
- Cost-control changes, backups, recovery, and retention/purge operations.
- Documentation or operational corrections that keep deployed behavior honest.

## Not Planned

- New product phases, recruiter marketplaces, or broad refactors.
- Billing/payOS activation without a separate explicit approval.
- Video recording or raw media retention.
- Emotion, personality, honesty, protected-attribute, or hiring-probability
  inference.

## Operational Ownership

| Area | Owner | Cadence |
|---|---|---|
| Production deployment and rollback | Nguyễn Đức Hoàng Phúc | on approved maintenance change |
| Secrets/provider credential rotation | Nguyễn Đức Hoàng Phúc | on incident or provider policy requirement |
| Realtime retention purge | Nguyễn Đức Hoàng Phúc | once per Asia/Ho_Chi_Minh calendar day while production is online |
| Dependency issue review, including issue #103 | Nguyễn Đức Hoàng Phúc | monthly and before affected feature adoption |
| Backup/recovery and privacy incident response | Nguyễn Đức Hoàng Phúc | monthly readiness review and on incident |

The temporary production retention mechanism is a manual daily operator process
until a no-surprise scheduled service is approved. Each daily run begins with:

```bash
python scripts/purge_realtime_interviews.py --retention-days 30 --batch-limit 500
```

Only after reviewing the dry-run count and target environment may the owner run
one bounded production batch with `--execute`. The closeout session ran only the
dry-run and did not perform a broad purge. A future Render Cron Job may replace
the manual cadence after its cost, timezone, alerting, and disable procedure are
reviewed.

[Issue #103](https://github.com/aumi102/cvfit/issues/103) is a non-blocking
accepted maintenance risk for the current Phase 8 path. It tracks the remaining
Next.js/transitive Sharp advisory chain and must be reassessed before image
processing is introduced, when a compatible upstream fix is available, or at
the monthly dependency review. It is not hidden or treated as resolved.

## Cost Control

- Disable realtime immediately with `ENABLE_REALTIME_INTERVIEW=false` when
  provider cost, abuse, or availability is unacceptable.
- Review OpenAI usage/budget and Render utilization monthly.
- Scale down or suspend Render services when the portfolio is inactive.
- Billing/payOS remains independent and disabled unless separately re-approved.
- Never put a server provider credential in the frontend to bypass an outage.

## Rollback

1. Disable realtime creation with the feature flag.
2. Roll frontend, backend, and worker to a documented compatible runtime SHA.
3. Do not downgrade the Phase 8 migration for a documentation or CORS rollback.
4. Disable the purge schedule/manual execution separately.
5. Re-run health, build identity, database-head, and read-only smoke checks.

## Archive Procedure

1. Disable realtime and public mutation paths.
2. Complete retention/deletion obligations or export only legally approved data.
3. Revoke OpenAI, Render, database, storage, OAuth, and other production
   credentials after dependency review.
4. Preserve source code and non-sensitive documentation; do not archive secrets,
   CVs, transcripts, audio, or tokens.
5. Suspend Render services and managed resources after backup/data review.
6. Archive the repository only after data, credential, issue, and recovery
   ownership are reconciled.

## Review Cadence

Perform one maintenance review per month while production remains online. The
review covers service health/cost, provider usage, retention dry-run/execution
evidence, backups, dependency issue #103, expiring credentials, and privacy
incidents. This is an owner-operated portfolio project, not a 24/7 service.

The authoritative Phase 8 evidence is in
[phase8_team_closeout.md](phase8_team_closeout.md) and
[phase8_production_closeout_smoke_report.md](phase8_production_closeout_smoke_report.md).
