# Phase 8 Realtime Interview Privacy Review

**Decision date:** 2026-07-22  
**Decision status:** implemented proposal; independent reviewer approval is
required on the replacement PR before Phase 8 closeout.

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

- Operational scheduling of the purge command must be configured and verified
  after deployment; this session does not execute a production purge.
- A database backup may retain deleted rows according to the infrastructure
  provider's backup lifecycle. The production privacy notice must state that
  limitation and the operator must follow the provider's approved backup policy.
- Browser-to-provider WebRTC is a policy boundary, not cryptographic proof that
  a modified browser never changed provider-side state.

## Sign-off

| Role | Evidence | State |
|---|---|---|
| Implementation owner | code, automated ownership/cascade tests, this decision | complete |
| QA/privacy reviewer (Đạt or delegate) | independent review on replacement PR | pending |
| Product/team acceptance | controlled deployed deletion and smoke evidence | pending |

This document does not use “approved” until both pending rows have reproducible
evidence.
