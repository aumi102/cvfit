# Realtime Interview Backend Implementation Report — Phase 8

**Updated:** 2026-07-21

**Owner:** Phúc

**Branch:** `phase8/phuc-reconciliation-completion`

**Starting main HEAD:** `21f99c2a5e643c9101a35fc901610c9bb95a6e67`

**Status:** Phúc backend scope implemented and CI-verified; team integration and live evidence remain

This report is limited to repository code and isolated validation. It does not
claim frontend completion, rubric-quality approval, privacy approval,
production deployment, production migration, or live OpenAI Realtime smoke.

## Reconciliation and canonical contract

The merged PR #99 implementation on `main` is the baseline. The canonical
contract is seven authenticated routes under `/v1/interview/realtime`, four
Phase 8 tables, and the lifecycle `setup -> ready -> active -> completed` with
terminal `aborted` and `failed` states. The detailed decision is in
`docs/phase8_repository_reconciliation.md`.

`origin/DLIGHT_Phase8_Finish` is not merge-compatible: it expects obsolete
`/start`, `/turns`, media deletion, a fifth media-artifact model, different
status/flag names, and local test stubs. Its human QA scenarios may be salvaged
selectively after rebasing to the canonical contract.

## Backend work completed

- Preserved the seven-route PR #99 API and four-table migration; no replacement
  route or media table was introduced.
- Retained JWT authentication, owner-filtered session lookup, cross-owner `404`,
  and linked application/analysis ownership checks.
- Kept `ENABLE_REALTIME_INTERVIEW=false` as the default and kept missing OpenAI
  configuration isolated to the client-secret route.
- Rejects `consent_recording=true`; this backend has no audio/video storage or
  deletion endpoint.
- Added a server-owned provider configuration builder with validated operator
  model, voice, transcription model, fixed tools policy, bounded instructions,
  and version `realtime_session_v1`.
- Added configurable client-secret TTL and a persisted per-session issuance
  interval. Neither server API keys nor ephemeral values are persisted/logged.
- Requires event sequences starting at zero and increasing by one. An exact
  sequence/type/hash replay is idempotent; conflicts and gaps fail closed.
- Persists only allowlisted/minimized event metadata and transcript turns with
  `client_reported_validated` provenance. Browser events are not described as
  provider-attested.
- Makes completion idempotent and preserves completed turns during summary
  retry.
- Adds a bounded server-side deterministic practice evaluator with rubric
  `realtime_practice_v1`, evaluator provenance, dimension evidence turn IDs,
  ready/pending/failed states, and a safe failure code.
- Keeps learning-roadmap output as proposals only; it does not auto-create or
  mutate learning tasks. No billing, credit, or payOS behavior changed.
- Excludes emotion, personality, honesty/truthfulness, protected-attribute, and
  hiring-probability inference.

## Trust boundary

The browser may report allowlisted transcript/lifecycle events, but the backend
validates, bounds, minimizes, hashes, orders, and owner-scopes them. The browser
cannot submit score, rubric, evaluator provenance, provider key, model policy,
hidden instruction, owner, entitlement, or retention settings.

Official OpenAI documentation states that a direct WebRTC client can update
most Realtime session fields after a client secret is minted. The backend
builder and frontend contract therefore establish a strict product policy, but
do not claim cryptographic immutability. Enforcing immutable provider session
configuration would require a separately reviewed proxy/provider-control
architecture that conflicts with the approved no-SDP-proxy design.

## Database and runtime schema

- Previous head: `20260623_0001`.
- Current expected single head: `20260716_0001`.
- Phase 8 tables: sessions, turns, events, summaries only.
- Runtime schema and the standalone checker now use the same authoritative
  `app.db.init_db._required_schema()` contract and expected head.
- Draft PR #101 CI run `29796351253` passed `upgrade head`, downgrade to
  `20260623_0001`, upgrade to head again, Phase 8 PostgreSQL constraint/index
  inspection, Alembic current/head comparison, and the runtime schema validator
  on disposable `pgvector/pgvector:pg16`.
- No local or production migration was run in this work session. Local
  PostgreSQL verification remains infrastructure-blocked because Docker Desktop
  is not running.

## Environment and deployment contract

The flag remains disabled by default. When enabled, the backend requires the
server API key plus model, voice, transcription model, session/question bounds,
client-secret TTL, and issuance interval. Render validation also requires an
explicit non-default JWT secret and explicit credential-safe CORS origins.
Billing/credit gating stays disabled unless deliberately configured; enabling
credit gating without billing is rejected by the environment checker.

No Render service, Render environment variable, production database, provider
credential, or payment provider was accessed or changed.

## Tests and validation status

Added real-module tests for lifecycle/ownership, context ownership, consent,
provider configuration, sanitized provider failures, strict event validation,
sequence replay/conflict/order, idempotent completion, summary provenance and
failure retry, feature flags, environment contract, migration metadata, and
disposable PostgreSQL schema constraints. Tests use fakes/mocks and do not call
OpenAI or payOS.

Local compile validation succeeded before the documentation pass:

```text
python -m compileall -q -f backend/app backend/tests scripts/check_env_contract.py scripts/check_db_schema.py
exit 0
```

Local pytest execution is blocked, not passed: the repository pins Python 3.11,
but the machine exposes Python 3.14 and neither available interpreter has
pytest. Dependencies were not installed because the task forbids installation.
The final Python 3.11 CI run collected 686 backend tests: 685 passed, 0 failed,
and 1 PostgreSQL-only test skipped in the SQLite job. The separate disposable
PostgreSQL job ran all 3 Phase 8 migration-contract tests successfully and
passed the full migration cycle/schema validation. No paid provider was called.

## Handoffs

- Quân: `docs/interview_realtime_frontend_handoff.md`
- Đạt: `docs/interview_realtime_qa_evaluation_handoff.md`
- Shared API: `docs/interview_realtime_api_contract.md`
- Architecture: `docs/interview_realtime_backend_architecture.md`

## Remaining team work

- Quân implements the browser WebRTC/interview/summary UI against the frozen
  backend contract and must not send provider configuration overrides.
- Đạt runs security/privacy/quality evaluation, browser QA, malicious-event
  cases, and rubric-quality review using the supplied hooks.
- An operator supplies a non-production OpenAI credential only for an approved
  controlled smoke after tests, frontend integration, and privacy approval.
- Production migration, flag activation, and deployment remain separately
  approved operations.
