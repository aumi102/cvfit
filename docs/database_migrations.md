# Database Migrations

Phase 1C added an Alembic baseline so schema changes can be reviewed and applied deliberately. Phase 1D makes Alembic the intentional schema-management path: API and worker startup verify the schema, but no longer silently create tables or patch columns.

Current Alembic head:

```text
20260716_0001
```

Revision chain:

```text
20260522_0001 -> 20260531_0001 -> 20260606_0001 -> 20260610_0001
-> 20260610_0002 -> 20260610_0003 -> 20260618_0001 -> 20260619_0001
-> 20260620_0001 -> 20260622_0001 -> 20260623_0001 -> 20260716_0001
```

`20260531_0001` is the Phase 2 auth foundation migration. It creates the
`users` table, adds nullable `analysis_jobs.user_id`, adds the
`analysis_jobs.user_id -> users.id` foreign key, and adds indexes for
`users.email` and `analysis_jobs.user_id`.

`analysis_jobs.user_id` must stay nullable because guest jobs remain supported.
Guest mode still creates analysis jobs without an account.

`20260606_0001` is the Phase 4 analysis revision migration. It adds
`analysis_jobs.parent_job_id`, `analysis_jobs.analysis_group_id`, and
`analysis_jobs.revision_number`.

The later linear revisions add Application Workspace, application artifacts,
typed interview answers, Target Jobs, Learning/Interview Practice, share links,
Google-auth fields, and disabled-by-default billing models.

`20260716_0001` is the Phase 8 Realtime Interview migration. It follows
`20260623_0001` and adds exactly four tables: realtime sessions, turns, bounded
events, and summaries. It does not add a media-artifact table.

## Why Alembic Was Added

- Make database schema changes explicit and reviewable.
- Avoid relying on app startup side effects for schema creation or patching.
- Prepare for safer Render/PostgreSQL updates.
- Fail fast when a runtime database is missing schema or is not at Alembic head.

## Install Development Dependencies

From the repository root:

```bash
cd backend
pip install -r requirements-dev.txt
```

Alembic is installed by `backend/requirements.txt` so Render service shells can
run migrations with the deployed backend environment. It also remains in
`backend/requirements-dev.txt` through the dev dependency chain. Migrations are
still an operator action; API and worker startup must not run them
automatically.

## Run Migrations Locally

Set `DATABASE_URL` for the target local database, then run:

```bash
python scripts/run_alembic.py upgrade head
```

For the Docker Compose database, the default local app value is:

```env
DATABASE_URL=postgresql+psycopg2://cvfit:cvfit@localhost:5432/cvfit
```

Do not commit `.env` files or real database URLs.

To validate a disposable/local PostgreSQL database after upgrading:

```bash
python scripts/check_db_schema.py
```

The checker reads `DATABASE_URL`, imports the authoritative runtime schema from
`app.db.init_db`, reports required tables/columns, verifies the expected
Alembic head, reports whether `alembic_version` exists, and checks the
PostgreSQL `vector` extension. It does not print the database URL or secret
values.

CI has two database-related paths:

- The backend hygiene/test job uses SQLite in memory for tests and Alembic
  metadata checks.
- The PostgreSQL migration job starts a disposable `pgvector/pgvector:pg16`
  service, upgrades to head, downgrades Phase 8 to `20260623_0001`, upgrades to
  head again, inspects Phase 8 PostgreSQL foreign keys/unique constraints/index,
  verifies `alembic current` matches `alembic heads`, and runs the runtime
  schema checker against that disposable CI database.

The PostgreSQL CI job does not use Render `DATABASE_URL`, real secrets, Render
APIs, deploy commands, or adoption/stamp helpers. Production and Render
migrations remain operator-controlled.

API and worker startup are non-mutating. If the runtime database is empty,
missing a required column, or lacks the expected Alembic revision, startup fails
with a message such as:

```text
Database schema is not initialized. Run alembic upgrade head.
Database schema is not at Alembic head. Run alembic upgrade head.
```

For local Docker, start the database first, run the migration against the local
Postgres port, then start the API and worker:

```powershell
docker compose up --build -d postgres redis
$env:DATABASE_URL="postgresql+psycopg2://cvfit:cvfit@localhost:5432/cvfit"
python scripts/run_alembic.py upgrade head
docker compose up --build -d
```

Windows CMD equivalent:

```bat
docker compose up -d postgres redis
set "DATABASE_URL=postgresql+psycopg2://cvfit:cvfit@localhost:5432/cvfit"
set "REDIS_URL=redis://localhost:6379/0"
python scripts\run_alembic.py upgrade head
python scripts\run_alembic.py current
python scripts/check_db_schema.py
```

Disposable container validation, independent of any existing Compose volume:

```powershell
docker run --rm -d --name cvfit-auth-migration-check `
  -e POSTGRES_USER=cvfit `
  -e POSTGRES_PASSWORD=cvfit `
  -e POSTGRES_DB=cvfit `
  -p 55432:5432 `
  pgvector/pgvector:pg16

docker exec cvfit-auth-migration-check pg_isready -U cvfit -d cvfit

$env:DATABASE_URL="postgresql+psycopg2://cvfit:cvfit@localhost:55432/cvfit"
$env:REDIS_URL="redis://localhost:6379/0"
python scripts/run_alembic.py upgrade head
python scripts/run_alembic.py current
python scripts/check_db_schema.py

docker stop cvfit-auth-migration-check
```

Disposable CMD equivalent:

```bat
docker run --rm -d --name cvfit-auth-migration-check -e POSTGRES_USER=cvfit -e POSTGRES_PASSWORD=cvfit -e POSTGRES_DB=cvfit -p 55432:5432 pgvector/pgvector:pg16
docker exec cvfit-auth-migration-check pg_isready -U cvfit -d cvfit
set "DATABASE_URL=postgresql+psycopg2://cvfit:cvfit@localhost:55432/cvfit"
set "REDIS_URL=redis://localhost:6379/0"
python scripts\run_alembic.py upgrade head
python scripts\run_alembic.py current
python scripts/check_db_schema.py
docker stop cvfit-auth-migration-check
```

Optional local-only downgrade/re-upgrade validation on a disposable database:

```bat
set "DATABASE_URL=postgresql+psycopg2://cvfit:cvfit@localhost:55432/cvfit"
set "REDIS_URL=redis://localhost:6379/0"
alembic downgrade 20260623_0001
python scripts\run_alembic.py current
python scripts\run_alembic.py upgrade head
python scripts\run_alembic.py current
python scripts/check_db_schema.py
```

Do not run downgrade on production without explicit data-loss approval. The
Phase 8 downgrade removes all four realtime-interview tables and their data.

## Create A New Migration

After changing SQLAlchemy models:

```bash
cd backend
alembic revision --autogenerate -m "message"
```

Review the generated migration before applying it. Autogenerate is a starting point, not a substitute for checking the SQL operations.

When a new migration becomes the project head, update
`EXPECTED_ALEMBIC_HEAD` in `app.db.init_db`. The test suite checks this runtime
constant against `alembic heads` so startup validation cannot silently drift
behind the migration directory.

## Render Database Migration Safety

Before running migrations against a Render database:

1. Confirm the target `DATABASE_URL` points to the intended Render database.
2. Take a database backup or snapshot.
3. Inspect current schema without printing secrets:
   `python scripts/check_db_schema.py`.
4. Confirm current Alembic revision from a trusted shell:
   `python scripts/run_alembic.py current`.
5. Review the migration file.
6. Run the migration from a trusted local/dev environment with
   `backend/requirements.txt` installed.
7. Run `python scripts/check_db_schema.py` after migration.
8. Redeploy or restart API/worker only after the migration succeeds.

Example:

```bash
python scripts/run_alembic.py upgrade head
```

Never commit Render secrets, database URLs, JWT secrets, S3 credentials, or
copied dashboard values. Never paste `DATABASE_URL` or `JWT_SECRET_KEY` into
logs, screenshots, PR comments, or chats.

Required env vars for migration/runtime:

```env
DATABASE_URL=<target database URL>
REDIS_URL=<required by app settings/runtime checks>
JWT_SECRET_KEY=<required for runtime, not normally used by Alembic>
```

If Render DB is behind the current Alembic head, apply only the reviewed
migrations after backup and local/disposable validation.

If Render DB is already at the current Alembic head, do not run another
upgrade. Run the schema checker and proceed with deploy readiness checks.

## Existing Database Adoption Strategy

Use migrations differently depending on the database state:

- Empty database: run `python scripts/run_alembic.py upgrade head`.
- Existing database already created by `Base.metadata.create_all()`: do not blindly run the initial migration because it will try to create tables that already exist.
- Existing database with matching `20260522_0001` baseline schema but missing or
  wrong `alembic_version`: first verify the schema, then run
  `alembic stamp 20260522_0001`, then run
  `python scripts/run_alembic.py upgrade head` after backup and local
  validation.
- Existing database with schema matching the current head but missing or wrong
  `alembic_version`: stop and verify how that happened. If it is confirmed to
  match the current head exactly, stamp the current head only after backup and
  documented approval.
- Existing database with schema drift: stop and resolve the mismatch deliberately before stamping or upgrading.

For an old Render MVP database, take a backup first, verify the schema without
printing secrets, and only stamp if it matches the expected baseline:

```bash
python scripts/check_db_schema.py
cd backend
alembic stamp 20260522_0001
cd ..
python scripts/run_alembic.py upgrade head
python scripts/run_alembic.py current
```

### Render MVP Adoption Workflow

Treat the Render PostgreSQL database as production-like:

0. Take a Render Postgres backup or snapshot from the Render dashboard.
1. Set `DATABASE_URL` locally without echoing it.
2. Run the schema checker.
3. Run the safe adoption helper.
4. Verify Alembic's current revision.
5. Restart the Render API and worker only if needed by the deployment workflow.

Windows PowerShell:

```powershell
# Paste the Render internal or external PostgreSQL URL only into this shell variable.
# Do not echo it, commit it, or paste it into logs.
$env:DATABASE_URL = "<render-postgres-url>"

python scripts/check_db_schema.py
python scripts/adopt_existing_db_with_alembic.py

python scripts/run_alembic.py current
```

If the checker reports missing tables or columns, stop. Do not stamp. Fix the mismatch deliberately after identifying why the live schema differs from the baseline.

Do not run `python scripts/run_alembic.py upgrade head` on an existing database that was already created by the old `Base.metadata.create_all()` startup fallback unless you have first verified the schema and planned the adoption path. The initial migration creates the baseline tables and will collide with an already-populated MVP database. For an empty database only, `python scripts/run_alembic.py upgrade head` is appropriate; the adoption helper requires `--allow-empty-upgrade` before it will run that path.

The adoption helper and schema checker should be used carefully: a database at
an old baseline will be missing newer columns until migrations are applied. If
the live DB is behind the current head, the expected path is backup, verify the
current state, then `python scripts/run_alembic.py upgrade head`.

## pgvector Notes

The baseline migration runs:

```sql
CREATE EXTENSION IF NOT EXISTS vector
```

This is idempotent on PostgreSQL services that support pgvector. If the target database does not support the extension, choose a PostgreSQL provider/plan that does before deploying features that use vector columns.

## Runtime Schema Behavior

`app.db.init_db.init_db()` now performs a non-mutating runtime schema check. It
does not call `Base.metadata.create_all()`, does not create the `vector`
extension, and does not add missing columns such as `analysis_jobs.access_token_hash`.

If the schema is missing or outdated, run Alembic deliberately against the
intended local/disposable database. For existing production-like databases,
take a backup and run schema/adoption checks before any migration or stamp.
