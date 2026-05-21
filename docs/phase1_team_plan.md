# Phase 1 Team Plan

Phase 1 turns the verified Phase 0 baseline into a deployed MVP and creates a working team foundation. The team should avoid product rewrites during this phase and keep changes small enough to verify with tests and smoke runs.

## Owners

- Phúc: backend/deployment lead.
- Quân: frontend/UI owner.
- Đạt: backend quality/database/testing owner.

## Work Split

### Phúc: Deployment And Architecture

Owns:

- Render Web Service setup for FastAPI.
- Render Background Worker setup for Celery.
- Render Redis/Key Value and Postgres configuration.
- S3-compatible storage environment variables for API and worker.
- Deployed smoke-test runbook and result capture.
- Architecture docs update after deployment.

Deliverables:

- Render deployment checklist completed.
- Deployed `/health` check passes.
- Deployed upload to result to DOCX report flow passes.
- Environment variable inventory is documented without secrets.

### Quân: Frontend And UX

Owns:

- Upload and JD input polish.
- Loading/progress states for queued/running jobs.
- Error states for upload, create-score, failed jobs, and report download.
- Result dashboard layout for score breakdown.
- Report download UX.
- Basic responsive layout pass.

Deliverables:

- UI handles success, loading, empty, and error states.
- Result page/card clearly shows fit score, score components, matched skills, and missing skills.
- Report download button has disabled/loading/error states.
- UI smoke checklist passes locally and on deployed MVP.

### Đạt: Backend Quality, Database, And Testing

Owns:

- Access-token MVP for job/result/report access.
- Alembic migration baseline.
- Backend tests for access-token behavior, report download, S3 config validation, and failure paths.
- S3 cleanup checklist and retention notes.
- Repository hygiene checks before handoff.

Deliverables:

- Alembic baseline migration exists and can create the current schema.
- Access token is required for result/report access or equivalent MVP protection is documented and implemented.
- Test suite covers the new backend behavior.
- S3 cleanup checklist is documented.

## Suggested 5-Day Timeline

### Day 1: Planning And Branch Setup

- Confirm Phase 1 scope and owners.
- Create separate branches or clearly scoped PRs.
- Phúc prepares Render services and env var checklist.
- Quân maps current UI states and missing states.
- Đạt drafts Alembic/access-token approach.

### Day 2: Foundation Work

- Phúc configures Render services without secrets in code.
- Quân implements loading/error/report-download UI states.
- Đạt adds Alembic baseline and first backend tests.

### Day 3: Integration

- Phúc runs initial deployed health and smoke checks.
- Quân verifies frontend against local Docker and deployed API.
- Đạt completes access-token MVP and expands tests.

### Day 4: Hardening

- Fix integration bugs only.
- Run local Docker smoke test.
- Run S3-backed smoke test.
- Run deployed smoke test if Render services are ready.
- Update docs with actual commands and known limitations.

### Day 5: Demo Readiness

- Freeze Phase 1 scope.
- Confirm README and docs match the real workflow.
- Capture final smoke-test evidence.
- Review privacy, S3 cleanup, and known risks.
- Prepare Phase 2 backlog.

## Integration Checklist

- `python -m compileall backend/app` passes.
- `cd backend && python -m pytest` passes.
- `docker compose config` passes.
- Local Docker smoke test passes.
- S3-backed Docker smoke test passes.
- Deployed `/health` returns `{"status":"ok"}`.
- Deployed upload to result to report download flow passes.
- API and worker have matching `DATABASE_URL`, `REDIS_URL`, `STORAGE_BACKEND`, S3 variables, and `CV_MAX_UPLOAD_MB`.
- No secrets are committed.
- No generated uploads, reports, `__pycache__`, `.pyc`, local DB files, or model caches are tracked.
- README, deployment docs, and smoke-test docs reflect the actual commands used.
