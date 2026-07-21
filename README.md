# AI CV Fit App

FastAPI-based CV-to-job-description fit scoring MVP. The app uploads a CV, accepts pasted JD text, runs an async Celery job, stores results in PostgreSQL, and returns JSON plus a downloadable DOCX report.

## Folder Structure

```text
backend/
  app/                  FastAPI app, API routes, DB, services, workers
  tests/                pytest tests
  requirements.txt      backend Python dependencies
  requirements-ml.txt   ML runtime dependencies with CPU-only Torch
  requirements-dev.txt  local test/development dependencies
frontend/
  templates/            Jinja templates
  static/               vanilla JS/static assets
scripts/                smoke tests and operational scripts
docs/                   deployment and baseline docs
docker/                 API and worker Dockerfiles
docker-compose.yml      local API/worker/Postgres/Redis stack
```

## Architecture

FastAPI + Celery + Redis + PostgreSQL.

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

## Frontend Demo

The MVP frontend is served by the FastAPI backend from `frontend/templates` and
`frontend/static`; there is no separate Node/React/Next app or separate
frontend deployment. On Render, the demo URL is the backend Web Service root,
for example:

```text
https://cvfit.onrender.com/
```

The page uses same-origin API calls for the real MVP flow: upload a CV through
`/v1/cv/upload`, create a score job through `/v1/jobs/create-score`, poll job
status, fetch protected result/report metadata, and expose a DOCX report
download link. The repository now includes JWT account authentication and
owner-scoped product routes; legacy guest jobs retain per-job access-token
protection. Use only synthetic CV/JD data for demos. The current app has no
cleanup endpoint, so mutating demos create records and a report.

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
python -m compileall backend/app
cd backend && python -m pytest --basetemp pytest-cache-files-local -p no:cacheprovider
cd backend && alembic heads
cd backend && alembic history
docker compose config
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
python -m compileall backend/app
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

## Phase 8 Realtime Interview backend

The Phase 8 backend contract is seven authenticated owner-scoped routes under
`/v1/interview/realtime`. It mints a short-lived client secret so the browser
can connect directly to OpenAI Realtime over WebRTC; the backend never proxies
or stores SDP, raw audio, or video. Four tables store sessions, bounded turns,
minimized events, and versioned practice summaries.

`ENABLE_REALTIME_INTERVIEW=false` is the safe default. Do not enable it until
frontend integration, CI/PostgreSQL evidence, QA/evaluation, privacy approval,
an approved non-production credential, and a controlled smoke plan are all in
place. Backend contracts and handoffs:

- [API contract](docs/interview_realtime_api_contract.md)
- [Backend architecture](docs/interview_realtime_backend_architecture.md)
- [Frontend handoff](docs/interview_realtime_frontend_handoff.md)
- [QA/evaluation handoff](docs/interview_realtime_qa_evaluation_handoff.md)
- [Implementation report](docs/interview_realtime_backend_implementation_report.md)

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






