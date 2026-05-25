# Database Migrations

Phase 1C adds an Alembic baseline so schema changes can be reviewed and applied deliberately. The app still keeps its `Base.metadata.create_all()` startup fallback for MVP compatibility, but new schema changes should be represented as Alembic migrations.

## Why Alembic Was Added

- Make database schema changes explicit and reviewable.
- Avoid relying only on app startup side effects for future changes.
- Prepare for safer Render/PostgreSQL updates.
- Keep the current MVP startup path working while migration discipline is introduced.

## Install Development Dependencies

From the repository root:

```bash
cd backend
pip install -r requirements-dev.txt
```

Alembic is in `backend/requirements-dev.txt` because migrations are currently an operator/developer action, not part of normal API or worker startup. The Render API and worker runtime install remains `backend/requirements.txt`.

## Run Migrations Locally

Set `DATABASE_URL` for the target local database, then run:

```bash
cd backend
alembic upgrade head
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

The checker reads `DATABASE_URL`, reports required tables/columns, confirms `analysis_jobs.access_token_hash`, reports whether `alembic_version` exists, and checks the PostgreSQL `vector` extension. It does not print the database URL or secret values.

## Create A New Migration

After changing SQLAlchemy models:

```bash
cd backend
alembic revision --autogenerate -m "message"
```

Review the generated migration before applying it. Autogenerate is a starting point, not a substitute for checking the SQL operations.

## Render Database Migration Safety

Before running migrations against a Render database:

1. Confirm the target `DATABASE_URL` points to the intended Render database.
2. Take a database backup or snapshot.
3. Review the migration file.
4. Run the migration from a trusted local/dev environment with `backend/requirements-dev.txt` installed.
5. Redeploy or restart API/worker only after the migration succeeds.

Example:

```bash
cd backend
alembic upgrade head
```

Never commit Render secrets, database URLs, S3 credentials, or copied dashboard values.

## Existing Database Adoption Strategy

Use the initial migration differently depending on the database state:

- Empty database: run `alembic upgrade head`.
- Existing database already created by `Base.metadata.create_all()`: do not blindly run the initial migration because it will try to create tables that already exist.
- Existing database with matching baseline schema: first verify the schema, then run `alembic stamp head` to mark the database as current without recreating tables.
- Existing database with schema drift: stop and resolve the mismatch deliberately before stamping or upgrading.

For the current Render MVP database, take a backup first, verify the schema without printing secrets, and only stamp if it matches the baseline:

```bash
python scripts/check_db_schema.py
cd backend
alembic stamp head
alembic current
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

cd backend
alembic current
cd ..
```

If the checker reports missing tables or columns, stop. Do not stamp. Fix the mismatch deliberately after identifying why the live schema differs from the baseline.

Do not run `alembic upgrade head` on an existing database that was already created by `Base.metadata.create_all()`. The initial migration creates the baseline tables and will collide with an already-populated MVP database. For an empty database only, `alembic upgrade head` is appropriate; the adoption helper requires `--allow-empty-upgrade` before it will run that path.

Keep the app startup `create_all()` fallback temporarily until this workflow has been proven across local, Render, and any future production-like environments.

## pgvector Notes

The baseline migration runs:

```sql
CREATE EXTENSION IF NOT EXISTS vector
```

This is idempotent on PostgreSQL services that support pgvector. If the target database does not support the extension, choose a PostgreSQL provider/plan that does before deploying features that use vector columns.

## Current MVP Compatibility

`app.db.init_db.init_db()` still creates the vector extension and calls `Base.metadata.create_all()` during app startup. This remains intentionally for Phase 1 MVP compatibility with local Docker and Render deploys.

The temporary `access_token_hash` auto-column helper remains for databases created before the Alembic baseline existed. Remove this helper only after migrations are mandatory in every environment.
