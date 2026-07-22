# AI CV Fit App

AI CV Fit is a FastAPI + Next.js application for CV/JD analysis, job history,
interview practice, and a Vietnamese Realtime Voice/WebRTC interview. Celery
workers process CV analysis jobs; PostgreSQL stores owner-scoped product data.

## Folder Structure

```text
backend/
  app/                  FastAPI app, API routes, DB, services, workers
  tests/                pytest tests
  requirements.txt      backend Python dependencies
  requirements-ml.txt   ML runtime dependencies with CPU-only Torch
  requirements-dev.txt  local test/development dependencies
frontend/
  src/                  Next.js App Router UI and API client
  e2e/                  Playwright mocked browser regressions
  templates/, static/   legacy FastAPI-served fallback UI
scripts/                smoke tests and operational scripts
docs/                   deployment and baseline docs
docker/                 API and worker Dockerfiles
docker-compose.yml      local API/worker/Postgres/Redis stack
```

## Architecture

The deployed topology is a Next.js frontend, FastAPI API, Celery worker, Redis,
PostgreSQL/pgvector, and private S3-compatible object storage. Realtime audio
travels directly between the consented browser and OpenAI over WebRTC using a
short-lived credential minted by the backend; CV Fit never stores raw audio,
video, or SDP.

## Local Docker Run

For a fresh local Docker database, start Postgres and Redis first, run Alembic,
then start the API and worker:

```powershell
docker compose up --build -d postgres redis
cd backend
$env:DATABASE_URL="postgresql+psycopg2://cvfit:cvfit@localhost:5432/cvfit"
alembic upgrade head
cd ..
docker compose up --build -d
```

Open:

```text
http://localhost:8000
```

## Frontend

Run the Next.js application separately from FastAPI:

```bash
cd frontend
npm ci
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL` to the FastAPI origin. The legacy Jinja/vanilla
UI remains a fallback, not the primary product frontend. JWT users can open
stable history detail routes at `/history/[jobId]`, use Vietnamese text
practice, or enter the visible Realtime Voice mode. Use synthetic CV/JD and
interview content for demos.

Stop:
```bash
docker compose down
```

## Local Backend-Only Run

Start PostgreSQL and Redis separately, make sure `DATABASE_URL` points to that
local database, then:

```bash
cd backend
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

In another shell:

```bash
cd backend
celery -A app.workers.celery_app:celery_app worker --loglevel=INFO -Q cvfit
```

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest
```

There is intentionally no root requirements.txt; install from backend/requirements.txt for runtime or backend/requirements-dev.txt for local development and tests.

## CI Checks

GitHub Actions runs backend hygiene checks plus disposable PostgreSQL migration
validation on pull requests and pushes to `main`. The backend job uses only
safe local/test environment values:

```env
DATABASE_URL=sqlite+pysqlite:///:memory:
REDIS_URL=redis://localhost:6379/0
```

CI does not use Render `DATABASE_URL`, S3 credentials, API tokens, or any
production secret. Database migrations and existing production-like database
adoption remain operator-controlled; CI never upgrades or stamps Render
PostgreSQL.

The backend job checks:

```bash
python scripts/ci_guard.py
python -m compileall -q -f backend/app backend/tests scripts
python scripts/evaluate_phase8_rubric.py --check
cd backend && python -m pytest --basetemp pytest-cache-files-local -p no:cacheprovider
cd backend && alembic heads
cd backend && alembic history
docker compose config
cd frontend && npm run lint
cd frontend && npm test -- --run
cd frontend && npm run build
cd frontend && npm run test:e2e
```

The PostgreSQL migration job starts a disposable `pgvector/pgvector:pg16`
service with local CI-only credentials, runs `upgrade head`, downgrades Phase 8
to `20260623_0001`, upgrades to head again, inspects the Phase 8 PostgreSQL
constraints/indexes, verifies `alembic current` matches `alembic heads`, and
runs `python scripts/check_db_schema.py`. It does not use Render secrets, call
Render APIs, deploy, or run adoption/stamp helpers.

On Windows Anaconda Prompt, run the same local checks with:

```bat
set "DATABASE_URL=sqlite+pysqlite:///:memory:"
set "REDIS_URL=redis://localhost:6379/0"
set "PYTHONPYCACHEPREFIX=backend/pytest-cache-files-local/pycache-prefix"
python scripts/ci_guard.py
python -m compileall -q -f backend/app backend/tests scripts
python scripts/evaluate_phase8_rubric.py --check
cd backend
python -m pytest --basetemp pytest-cache-files-local -p no:cacheprovider
alembic heads
alembic history
cd ..
docker compose config
set "PYTHONPYCACHEPREFIX="
```

After a deploy, verify the public API without touching the database directly:

```bat
set "API_BASE_URL=https://your-render-api.onrender.com"
curl "%API_BASE_URL%/health"
```

## Database Migrations

Migration workflow and Render adoption notes are in [Database migrations](docs/database_migrations.md). For a disposable/local PostgreSQL validation run:

```bash
cd backend
DATABASE_URL=postgresql+psycopg2://cvfit:cvfit@localhost:5432/cvfit alembic upgrade head
cd ..
python scripts/check_db_schema.py
```

The current expected Alembic head is `20260716_0001`. It adds the four Phase 8
Realtime Interview tables after `20260623_0001`; the earlier authentication,
product, learning, and billing migrations remain in the single linear chain.

API and worker startup do not silently create or patch database tables. If the
schema is missing or behind Alembic head, startup fails with an error that tells
you to run `alembic upgrade head` against the intended local/disposable
database. Do not run migrations blindly against an existing production database
without a backup and schema/adoption checks.

## Phase 8 Realtime Interview

The Phase 8 backend contract is seven authenticated owner-scoped routes under
`/v1/interview/realtime`. It mints a short-lived client secret so the browser
can connect directly to OpenAI Realtime over WebRTC; the backend never proxies
or stores SDP, raw audio, or video. Four tables store sessions, bounded turns,
minimized events, and versioned practice summaries. The Next.js room implements
microphone consent, remote audio, live transcript, mute, bounded reconnect that
honors `Retry-After`, idempotent completion, summary polling, and owner-requested
hard deletion. New summaries use the Unicode-aware evaluator
`deterministic_transcript_v2_unicode`; Vietnamese, English, and mixed-language
synthetic fixtures run in CI.

`ENABLE_REALTIME_INTERVIEW=false` remains the fail-closed default for a fresh
environment. The reviewed Render production activation was verified at runtime
SHA `280cb96c0e6501cb42aa58eb5fae43c1e5022805` with backend-only provider
settings, HTTPS/CORS, and controlled synthetic text/voice/reconnect/history/
deletion smoke. Deletion remains available while the feature is disabled. The
retention policy is a 30-day maximum for the full realtime session graph,
enforced by a dry-run-first bounded operator purge.

- [API contract](docs/interview_realtime_api_contract.md)
- [Backend architecture](docs/interview_realtime_backend_architecture.md)
- [Frontend handoff](docs/interview_realtime_frontend_handoff.md)
- [QA/evaluation handoff](docs/interview_realtime_qa_evaluation_handoff.md)
- [Implementation report](docs/interview_realtime_backend_implementation_report.md)
- [Rubric evaluation](docs/phase8_rubric_evaluation_report.md)
- [Privacy and retention](docs/phase8_privacy_review.md)
- [Browser/device QA](docs/phase8_browser_device_qa_report.md)
- [Authoritative team closeout](docs/phase8_team_closeout.md)
- [Production closeout smoke](docs/phase8_production_closeout_smoke_report.md)
- [Maintenance/portfolio operating policy](docs/maintenance_mode.md)

AI CV Fit v1.0 is now owner-operated in Maintenance/Portfolio Mode. Nguyễn Đức
Hoàng Phúc is the sole maintainer; active feature phases are paused. Billing and
payOS remain outside Phase 8 and are not activated by this closeout. Dependency
issue [#103](https://github.com/aumi102/cvfit/issues/103) is a documented,
non-blocking maintenance risk rather than a resolved advisory.

## Smoke Test

With the Docker stack running:

```bash
python scripts/smoke_test_local.py
```

The smoke test uploads a temporary DOCX CV, creates a score job, waits for worker completion, validates result JSON, checks report metadata, and downloads a non-empty DOCX report.

For the deployed MVP, use the production-safe smoke script. The default mode is
read-only and calls only `/health`:

```bash
API_BASE_URL=https://your-render-api.onrender.com python scripts/smoke_test_mvp.py
```

Run the deployed end-to-end flow only with explicit opt-in and synthetic data:

```bash
API_BASE_URL=https://your-render-api.onrender.com SMOKE_ALLOW_MUTATING=1 python scripts/smoke_test_mvp.py --mutating
```

Do not set `DATABASE_URL` for deployed smoke tests, and do not use real CVs or
private personal data. Mutating smoke creates one tiny synthetic upload, score
job, and DOCX report; the current API has no cleanup endpoint.

## Phase 3 Result v2 Closeout

Phase 3 upgrades the app from a basic CV/JD scorer into an evidence-based CV fit
analyzer. Completed Phase 3 surfaces include Result JSON v2, score breakdown,
matched skills, missing skills, CV/JD evidence snippets, conditional
improvement actions, a Result Dashboard v2, DOCX report v2, an evaluation case
set, and guardrails v1.5.

Key closeout commands:

```bash
python -m pytest
python scripts/evaluate_scoring_cases.py
```

For deployed strict smoke, use only synthetic data:

```bash
API_BASE_URL=https://cvfit.onrender.com SMOKE_ALLOW_MUTATING=1 REQUIRE_RESULT_V2=1 python scripts/smoke_test_mvp.py --mutating
```

Windows `cmd.exe` equivalent:

```bat
cmd.exe /c "set API_BASE_URL=https://cvfit.onrender.com&& set SMOKE_ALLOW_MUTATING=1&& set REQUIRE_RESULT_V2=1&& python scripts\smoke_test_mvp.py --mutating"
```

Closeout references:

- [Result JSON v2 contract](docs/result_schema_v2.md)
- [Guardrails v1.5](docs/guardrails_v1_5.md)
- [Phase 3 closeout audit](docs/phase3_closeout_audit.md)
- [Phase 3 demo checklist](docs/phase3_demo_checklist.md)
- [Evaluation dataset](evaluation/README.md)

Known Phase 3.5 notes are intentionally small: keep strict smoke repeatable,
keep lint/build CI-safe, and use the demo checklist to show why evidence,
guardrails, and DOCX output make the product more trustworthy than a simple
keyword checker.

## Phase 0 Status

Phase 0 is closed as the current baseline. Verified items include the backend/frontend split, FastAPI API, Celery worker, Redis, PostgreSQL/pgvector, local/S3 storage abstraction, local Docker E2E smoke test, S3-backed Docker smoke test, result JSON, DOCX report download, safe report metadata, CPU-only Torch dependency path, and repository hygiene for generated files.

Current status: Phase 1A Render MVP smoke test has passed. Phase 1B access-token MVP passed local and Render smoke tests.

Key docs:

- [Phase 0 baseline](docs/phase0_baseline.md)
- [Roadmap](docs/roadmap.md)
- [Phase 1 team plan](docs/phase1_team_plan.md)
- [Render deployment guide](docs/render_deployment.md)
- [Render manual setup checklist](docs/render_manual_setup_checklist.md)
- [Phase 1 Render execution runbook](docs/phase1_render_execution.md)
- [Database migrations](docs/database_migrations.md)
- [S3 smoke test guide](docs/s3_smoke_test.md)






