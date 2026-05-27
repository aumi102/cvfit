# Codex Prompts — AI CV Fit Phase 1

## Prompt 1 — Add Phase 1 docs

```text
You are working on the AI CV Fit App repository.

Goal:
Add Phase 1 closeout documentation without changing runtime behavior.

Tasks:
1. Create docs/phase1-closeout-checklist.md with a checklist covering deploy, worker, S3, access token protection, API contract, Next frontend integration, Alembic validation, S3 lifecycle cleanup, runbook, Phase 2 spec, and demo fallback.
2. Create docs/api-contract-next.md documenting:
   - backend base URLs
   - CORS requirements
   - POST /v1/cv/upload
   - POST /v1/jobs/create-score
   - GET /v1/jobs/{job_id}
   - GET /v1/jobs/{job_id}/result?access_token=...
   - GET /v1/jobs/{job_id}/report?access_token=...
   - GET /v1/jobs/{job_id}/report/download?access_token=...
   - access_token handling rules: never log token, result/report/download require token.
3. Create docs/phase2-product-spec.md with product roadmap:
   - result dashboard
   - evidence-based feedback
   - safe CV rewrite assistant
   - interview readiness
   - career roadmap
   - user history.
4. Create docs/guardrails.md covering:
   - upload guardrails
   - privacy guardrails
   - output guardrails
   - rewrite no-fabrication guardrails.
5. Do not modify app code.
6. Run markdown lint if available; otherwise just ensure files are readable.

Output:
- list files created
- summarize docs
- mention no runtime behavior changed
```

## Prompt 2 — Audit access token enforcement

```text
You are auditing the AI CV Fit App backend.

Goal:
Verify that result/report/download endpoints are protected by access_token.

Tasks:
1. Find all routes for job status, result, report preview, and report download.
2. Confirm which endpoints require access_token.
3. Ensure status endpoint does not expose sensitive result/report content.
4. Ensure result/report/download reject:
   - missing access_token
   - wrong access_token
   - token for another job
5. Ensure access_token is not logged.
6. Ensure error responses do not leak local paths, S3 keys, raw CV text, or stack traces.
7. Add or update tests for:
   - missing token → 401/403
   - wrong token → 401/403
   - correct token → 200
   - token for job A cannot access job B.
8. Keep API contract backward-compatible if current frontend depends on it.
9. Run tests.

Output:
- files changed
- tests added
- test command and result
- any remaining risk
```

## Prompt 3 — Validate Alembic baseline safely

```text
You are auditing database migrations for the AI CV Fit App.

Goal:
Make Alembic migration validation safe and repeatable before Phase 1 closeout.

Tasks:
1. Inspect alembic.ini, migrations folder, SQLAlchemy models, and app DB initialization.
2. Document the current migration state.
3. Add docs/alembic-validation-runbook.md with:
   - never run first migration test on production DB
   - use disposable DB
   - commands: alembic current/history/upgrade head/current
   - smoke test after migration
   - production caution about schema drift and alembic_version.
4. If tests are missing, add a lightweight migration smoke test if feasible without external production DB.
5. Do not stamp production DB automatically.
6. Do not remove existing tables/data.
7. Run backend tests.

Output:
- migration state summary
- docs created/updated
- test result
- recommendation: ready/not ready for production migration
```

## Prompt 4 — Add S3 cleanup runbook/policy

```text
You are improving storage hygiene for the AI CV Fit App.

Goal:
Add S3 lifecycle cleanup policy and runbook without changing app runtime behavior.

Tasks:
1. Create infra/s3-lifecycle.json with rules:
   - expire tmp/ after 1 day
   - expire uploads/raw-cv/ after 30 days
   - expire reports/ after 30 days
   - abort incomplete multipart uploads after 7 days
2. Create docs/s3-cleanup-runbook.md with:
   - reason: CV/report may contain personal data
   - AWS CLI put-bucket-lifecycle-configuration command
   - get-bucket-lifecycle-configuration verification command
   - privacy checklist: no raw CV logs, no access token logs, no local_path exposure.
3. Do not hard-code secrets.
4. Use env placeholders for bucket and region.

Output:
- files created
- exact command for applying policy
- note that policy must be applied manually by someone with AWS permissions
```

## Prompt 5 — Frontend integration acceptance audit

```text
You are auditing the Next/React frontend integration for AI CV Fit App.

Goal:
Ensure the Phase 1 frontend can demo the core flow against the real backend.

Tasks:
1. Find the frontend API client.
2. Ensure API base URL comes from NEXT_PUBLIC_API_BASE_URL.
3. Implement or verify pages:
   - landing page
   - analyze page with CV upload + JD textarea
   - job loading/result page
   - report download button.
4. Ensure create-score response stores job_id and access_token.
5. Ensure access_token is never console.logged.
6. Implement error states for upload fail, job fail, result fail, download fail.
7. Poll job status every 2–3 seconds and stop on succeeded/failed.
8. Keep Jinja backend UI untouched as fallback.
9. Run npm build and TypeScript check.

Output:
- files changed
- screenshots or route list
- npm build result
- known limitations
```
