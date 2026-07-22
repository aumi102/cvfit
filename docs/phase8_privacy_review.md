# Phase 8 Realtime Interview Privacy Review

**Decision date:** 2026-07-22  
**Decision status:** accepted by the project owner for owner-operated
Maintenance/Portfolio Mode. PR #104 has recorded reviewer approval; this is an
operational privacy decision, not legal certification or a new former-team
signature.

## Data-Minimization Decision

| Data | Retention | Deletion behavior |
|---|---|---|
| Session metadata | 30 days after `updated_at` | hard delete |
| Validated client events | same as parent session | cascade hard delete |
| Transcript turns | same as parent session | cascade hard delete |
| Deterministic summary | same as parent session | cascade hard delete |
| Raw audio/video | never stored | not applicable |
| SDP/provider payload | never stored | not applicable |
| Ephemeral/provider credential | memory only; never persisted | expires and is discarded |

Thirty days is the maximum operational retention for realtime practice data.
Users may delete their own session earlier from the summary UI or the
owner-scoped privacy endpoint. Deletion is intentionally a hard delete rather
than anonymization because transcript content can remain identifying even after
account identifiers are removed.

## Controls Reviewed

- `DELETE /v1/interview/realtime/sessions/{id}` is JWT authenticated,
  owner-scoped, idempotent, and non-disclosing: missing or cross-owner IDs return
  the same `204` result.
- Deleting a realtime session cascades only its turns, events, and summary. It
  does not delete the linked application, target job, CV, or account.
- Privacy deletion remains available when the realtime creation feature flag is
  disabled.
- The bounded purge service uses batches of at most 500. The operator script is
  dry-run by default and logs counts/cutoff only, never IDs or transcript text.
- Microphone consent is required before a client credential is requested.
- Recording requests, SDP, binary audio/video, provider JSON, overall score from
  the client, and arbitrary payload fields are rejected or never accepted.
- No current analytics integration receives transcript content or credentials.
  Future analytics must preserve that prohibition.
- Application logs must not contain transcript text, raw provider errors,
  authorization headers, or ephemeral credentials.

## Sensitive Inference Review

The server-owned rubric explicitly excludes emotion, personality, honesty,
protected attributes, and hiring-outcome prediction. Learning tasks are
proposals only and cannot mutate a roadmap automatically.

## Residual Risks

- Purge ownership is concentrated in the sole maintainer. Until an approved
  Render Cron Job replaces it, the control is one manual dry-run-first operator
  check per Asia/Ho_Chi_Minh calendar day. Missed checks are an operational
  risk and must be reconciled at the next maintenance review.
- A database backup may retain deleted rows according to the infrastructure
  provider's backup lifecycle. The production privacy notice must state that
  limitation and the operator must follow the provider's approved backup policy.
- Browser-to-provider WebRTC is a policy boundary, not cryptographic proof that
  a modified browser never changed provider-side state.

## Sign-off

| Role | Evidence | State |
|---|---|---|
| Implementation owner | code, automated ownership/cascade tests, this decision | complete |
| Replacement review | PR #104 `reviewDecision=APPROVED`, CI green, merged | complete |
| Product-owner acceptance | controlled deployed deletion/cascade, retention dry-run, smoke, and statement below | complete |

Production deletion was exercised only with a synthetic session. Owner delete
returned `204`, repeat delete remained safe, and a read-only DB check found zero
session/event/turn/summary child rows while the linked application remained.
The production retention command was dry-run only: zero candidates and zero
deletions, with no IDs or transcript content printed. Cross-owner protection is
covered by tests against production modules.

> Tôi, Nguyễn Đức Hoàng Phúc, với vai trò project owner và sole maintainer của AI CV Fit sau Phase 8, xác nhận đã xem xét kết quả CI, production deployment, synthetic smoke, QA và privacy controls. Tôi chấp nhận Phase 8 cho mục đích vận hành ở Maintenance/Portfolio Mode, với retention tối đa 30 ngày, owner-scoped deletion, không lưu raw audio/video/SDP và không thực hiện sensitive inference. Xác nhận này không phải chứng nhận pháp lý và không đại diện cho chữ ký mới của các thành viên cũ.

The sole maintainer owns daily purge evidence, backup-policy review, incident
handling, and archival execution. Detailed commands and rollback boundaries are
in [phase8_data_retention_and_deletion.md](phase8_data_retention_and_deletion.md)
and [maintenance_mode.md](maintenance_mode.md).
