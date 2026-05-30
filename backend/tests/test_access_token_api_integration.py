"""Extended API integration tests for access-token protection and edge cases.

These tests complement the existing coverage in test_storage.py by focusing on:
- Result/report endpoints when job is not ready
- Missing report_docx_path
- Job status endpoint (public, no token required)
- cv_id alias support in ScoreCreateRequest
- Token-only endpoints: result and report require token; status does not
"""

import os
import sys
import uuid
from types import SimpleNamespace
from io import BytesIO

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from fastapi import HTTPException

from app.api.routes import jobs as jobs_route
from app.schemas.requests import ScoreCreateRequest, ScoreOptions


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash(token: str) -> str:
    return jobs_route._hash_access_token(token)


# ---------------------------------------------------------------------------
# Job status endpoint — public, no token required
# ---------------------------------------------------------------------------

def test_job_status_returns_public_info_without_token():
    """Status endpoint must not require token (it is used by polling)."""
    job_id = str(uuid.uuid4())
    fake_job = SimpleNamespace(
        id=uuid.UUID(job_id),
        status="running",
        progress=45,
        error_message=None,
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    response = jobs_route.job_status(job_id, db=fake_db)

    assert response.job_id == job_id
    assert response.status == "running"
    assert response.progress == 45
    assert response.error_message is None
    assert response.error is None


def test_job_status_returns_error_message_when_job_failed():
    job_id = str(uuid.uuid4())
    fake_job = SimpleNamespace(
        id=uuid.UUID(job_id),
        status="failed",
        progress=50,
        error_message="Celery task timed out",
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    response = jobs_route.job_status(job_id, db=fake_db)

    assert response.status == "failed"
    assert response.error_message == "Celery task timed out"
    assert response.error == "Celery task timed out"


def test_job_status_returns_404_for_unknown_job():
    fake_db = SimpleNamespace(get=lambda model, key: None)

    with pytest.raises(HTTPException) as exc:
        jobs_route.job_status(str(uuid.uuid4()), db=fake_db)

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()


# ---------------------------------------------------------------------------
# Result endpoint — token required; job must be succeeded + have result_json
# ---------------------------------------------------------------------------

def test_result_endpoint_returns_409_when_job_is_queued():
    """Result should not be accessible while job is still queued."""
    job_id = str(uuid.uuid4())
    token = "token-queued"
    fake_job = SimpleNamespace(
        status="queued",
        result_json=None,
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    with pytest.raises(HTTPException) as exc:
        jobs_route.job_result(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 409
    assert "not ready" in exc.value.detail.lower()


def test_result_endpoint_returns_409_when_job_is_running():
    job_id = str(uuid.uuid4())
    token = "token-running"
    fake_job = SimpleNamespace(
        status="running",
        result_json=None,
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    with pytest.raises(HTTPException) as exc:
        jobs_route.job_result(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 409
    assert "not ready" in exc.value.detail.lower()


def test_result_endpoint_returns_409_when_job_failed():
    """Even if result_json is None on failure, result endpoint returns 409."""
    job_id = str(uuid.uuid4())
    token = "token-failed"
    fake_job = SimpleNamespace(
        status="failed",
        result_json=None,
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    with pytest.raises(HTTPException) as exc:
        jobs_route.job_result(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 409


def test_result_endpoint_returns_409_when_succeeded_but_no_result_json():
    """An edge case: job marked succeeded but result_json is None."""
    job_id = str(uuid.uuid4())
    token = "token-no-result"
    fake_job = SimpleNamespace(
        status="succeeded",
        result_json=None,
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    with pytest.raises(HTTPException) as exc:
        jobs_route.job_result(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 409


def test_result_endpoint_succeeds_when_job_is_succeeded():
    job_id = str(uuid.uuid4())
    token = "token-ok"
    result_json = {"scores": {"fit_score": 85}, "skills": {}}
    fake_job = SimpleNamespace(
        status="succeeded",
        result_json=result_json,
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    response = jobs_route.job_result(job_id, access_token=token, db=fake_db)

    assert response.job_id == job_id
    assert response.result == result_json
    assert response.overall_fit_score == 85


# ---------------------------------------------------------------------------
# Report endpoint — token required; report_docx_path must be set
# ---------------------------------------------------------------------------

def test_report_endpoint_returns_409_when_report_not_ready():
    """Report metadata should not be accessible if report file is missing."""
    job_id = str(uuid.uuid4())
    token = "token-no-report"
    fake_job = SimpleNamespace(
        status="succeeded",
        report_docx_path=None,
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    with pytest.raises(HTTPException) as exc:
        jobs_route.job_report(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 409
    assert "not ready" in exc.value.detail.lower()


def test_report_endpoint_succeeds_when_report_is_ready():
    job_id = str(uuid.uuid4())
    token = "token-report-ok"
    fake_job = SimpleNamespace(
        status="succeeded",
        report_docx_path="reports/test.docx",
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    response = jobs_route.job_report(job_id, access_token=token, db=fake_db)

    assert response["job_id"] == job_id
    assert response["report_status"] == "ready"
    assert response["format"] == "docx"
    assert f"/v1/jobs/{job_id}/report/download?access_token={token}" == response["download_url"]


# ---------------------------------------------------------------------------
# Report download endpoint — token required; job must be succeeded
# ---------------------------------------------------------------------------

def test_download_returns_409_when_job_is_queued(monkeypatch):
    """Download should not work for non-succeeded jobs."""
    job_id = str(uuid.uuid4())
    token = "token-dl-queued"
    fake_job = SimpleNamespace(
        status="queued",
        report_docx_path="reports/test.docx",
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)
    fake_storage = SimpleNamespace(read_bytes=lambda loc: b"fake-docx")
    monkeypatch.setattr(jobs_route, "get_storage", lambda: fake_storage)

    with pytest.raises(HTTPException) as exc:
        jobs_route.download_docx(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 409


def test_download_returns_409_when_job_is_running(monkeypatch):
    job_id = str(uuid.uuid4())
    token = "token-dl-running"
    fake_job = SimpleNamespace(
        status="running",
        report_docx_path="reports/test.docx",
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)
    fake_storage = SimpleNamespace(read_bytes=lambda loc: b"fake-docx")
    monkeypatch.setattr(jobs_route, "get_storage", lambda: fake_storage)

    with pytest.raises(HTTPException) as exc:
        jobs_route.download_docx(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 409


def test_download_returns_409_when_job_failed(monkeypatch):
    job_id = str(uuid.uuid4())
    token = "token-dl-failed"
    fake_job = SimpleNamespace(
        status="failed",
        report_docx_path="reports/test.docx",
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)
    fake_storage = SimpleNamespace(read_bytes=lambda loc: b"fake-docx")
    monkeypatch.setattr(jobs_route, "get_storage", lambda: fake_storage)

    with pytest.raises(HTTPException) as exc:
        jobs_route.download_docx(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 409


def test_download_returns_409_when_report_docx_path_is_none(monkeypatch):
    job_id = str(uuid.uuid4())
    token = "token-dl-no-path"
    fake_job = SimpleNamespace(
        status="succeeded",
        report_docx_path=None,
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)
    fake_storage = SimpleNamespace(read_bytes=lambda loc: b"fake-docx")
    monkeypatch.setattr(jobs_route, "get_storage", lambda: fake_storage)

    with pytest.raises(HTTPException) as exc:
        jobs_route.download_docx(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 409


# ---------------------------------------------------------------------------
# Token edge cases
# ---------------------------------------------------------------------------

def test_result_endpoint_returns_403_when_token_is_empty_string():
    """Empty token string should be treated as missing."""
    job_id = str(uuid.uuid4())
    fake_job = SimpleNamespace(
        status="succeeded",
        result_json={"scores": {"fit_score": 90}},
        access_token_hash=_hash("real-token"),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    with pytest.raises(HTTPException) as exc:
        jobs_route.job_result(job_id, access_token="", db=fake_db)

    assert exc.value.status_code == 403


def test_report_endpoint_returns_403_when_token_is_empty_string():
    job_id = str(uuid.uuid4())
    fake_job = SimpleNamespace(
        status="succeeded",
        report_docx_path="reports/test.docx",
        access_token_hash=_hash("real-token"),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    with pytest.raises(HTTPException) as exc:
        jobs_route.job_report(job_id, access_token="", db=fake_db)

    assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# cv_id / cv_file_id alias support
# ---------------------------------------------------------------------------

def test_result_contract_extracts_all_score_fields():
    """Verify _result_contract_fields maps all nested score keys."""
    job_id = str(uuid.uuid4())
    token = "token-all-scores"
    result_json = {
        "scores": {
            "fit_score": 78,
            "experience_score": 65,
            "skill_score": 90,
        },
        "skills": {
            "matched_must_groups": ["Python", "FastAPI"],
            "matched_nice_groups": ["Docker"],
        },
        "skill_gap": {
            "missing_must_have": ["Kubernetes"],
            "missing_nice_to_have": ["AWS"],
            "learn_suggestions": ["Learn Kubernetes basics"],
        },
        "cv_improvements": ["Add more project details"],
        "evidence": [{"type": "skill_match", "detail": "Python found at line 3"}],
    }
    fake_job = SimpleNamespace(
        status="succeeded",
        result_json=result_json,
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    response = jobs_route.job_result(job_id, access_token=token, db=fake_db)

    assert response.overall_fit_score == 78
    assert "Python" in response.strengths
    assert "FastAPI" in response.strengths
    assert "Kubernetes" in response.missing_skills
    assert "AWS" in response.missing_skills
    assert "Learn Kubernetes basics" in response.recommendations
    assert "Add more project details" in response.recommendations
    assert len(response.evidence) == 1


# ---------------------------------------------------------------------------
# 404 for unknown job across all token-gated endpoints
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "endpoint,token",
    [
        ("job_result", "some-token"),
        ("job_report", "some-token"),
        ("download_docx", "some-token"),
    ],
)
def test_all_token_gated_endpoints_return_404_for_unknown_job(endpoint, token, monkeypatch):
    fake_db = SimpleNamespace(get=lambda model, key: None)
    if endpoint == "download_docx":
        monkeypatch.setattr(jobs_route, "get_storage", lambda: SimpleNamespace(read_bytes=lambda loc: b"x"))

    with pytest.raises(HTTPException) as exc:
        getattr(jobs_route, endpoint)(str(uuid.uuid4()), access_token=token, db=fake_db)

    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# create-score endpoint — validation
# ---------------------------------------------------------------------------

def test_create_score_job_returns_404_for_unknown_cv_file():
    """POST /create-score must return 404 when cv_file_id does not exist."""
    fake_db = SimpleNamespace(get=lambda model, key: None)
    payload = ScoreCreateRequest(
        cv_file_id=str(uuid.uuid4()),
        jd_text="x" * 30,
        options=ScoreOptions(target_role="Backend Engineer"),
    )

    with pytest.raises(HTTPException) as exc:
        jobs_route.create_score_job(payload, db=fake_db)

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()


def test_create_score_job_returns_job_id_and_access_token(monkeypatch):
    """create_score_job must return job_id and access_token (>= 32 chars)."""
    fake_cv = SimpleNamespace(id=uuid.uuid4())
    enqueued = []

    class FakeDb:
        def get(self, model, key):
            return fake_cv

        def add(self, row):
            pass

        def flush(self):
            pass

        def commit(self):
            pass

    fake_task_module = SimpleNamespace(
        __name__="app.workers.tasks",
        run_job=SimpleNamespace(delay=lambda jid: enqueued.append(jid)),
    )
    monkeypatch.setitem(sys.modules, "app.workers.tasks", fake_task_module)

    payload = ScoreCreateRequest(
        cv_file_id=str(fake_cv.id),
        jd_text="x" * 30,
        options=ScoreOptions(target_role="Backend Engineer"),
    )

    response = jobs_route.create_score_job(payload, db=FakeDb())

    assert response.job_id
    assert response.access_token
    assert len(response.access_token) >= 32


# ---------------------------------------------------------------------------
# Token expiration
# ---------------------------------------------------------------------------

def test_result_endpoint_returns_403_when_token_expired(monkeypatch):
    """Expired token must return 403."""
    from datetime import datetime, timedelta, UTC
    import app.api.routes.jobs as jobs_mod

    job_id = str(uuid.uuid4())
    token = "token-expired"
    past = datetime.now(UTC) - timedelta(hours=1)
    fake_job = SimpleNamespace(
        status="succeeded",
        result_json={"scores": {"fit_score": 85}},
        access_token_hash=_hash(token),
        access_token_expires_at=past,
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    with pytest.raises(HTTPException) as exc:
        jobs_mod.job_result(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 403
    assert "expired" in exc.value.detail.lower()


def test_result_endpoint_allows_valid_non_expiring_token(monkeypatch):
    """Token with expires_at=None must be accepted."""
    job_id = str(uuid.uuid4())
    token = "token-no-expiry"
    fake_job = SimpleNamespace(
        status="succeeded",
        result_json={"scores": {"fit_score": 85}},
        access_token_hash=_hash(token),
        access_token_expires_at=None,
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    response = jobs_route.job_result(job_id, access_token=token, db=fake_db)

    assert response.overall_fit_score == 85


# ---------------------------------------------------------------------------
# Download: StorageNotFoundError edge case
# ---------------------------------------------------------------------------

def test_download_returns_404_when_storage_file_missing(monkeypatch):
    """When report_docx_path is set but file is gone from storage, return 404."""
    from app.services.storage import StorageNotFoundError

    job_id = str(uuid.uuid4())
    token = "token-file-gone"
    fake_job = SimpleNamespace(
        status="succeeded",
        report_docx_path="reports/old_job.docx",
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    def raise_not_found(loc):
        raise StorageNotFoundError(loc)

    fake_storage = SimpleNamespace(read_bytes=raise_not_found)
    monkeypatch.setattr(jobs_route, "get_storage", lambda: fake_storage)

    with pytest.raises(HTTPException) as exc:
        jobs_route.download_docx(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()


# ---------------------------------------------------------------------------
# Report endpoint: succeeded but no report_docx_path
# ---------------------------------------------------------------------------

def test_report_endpoint_returns_409_when_succeeded_but_no_docx_path():
    """Job status='succeeded' but report_docx_path is None → 409."""
    job_id = str(uuid.uuid4())
    token = "token-no-docx"
    fake_job = SimpleNamespace(
        status="succeeded",
        report_docx_path=None,
        access_token_hash=_hash(token),
    )
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    with pytest.raises(HTTPException) as exc:
        jobs_route.job_report(job_id, access_token=token, db=fake_db)

    assert exc.value.status_code == 409
    assert "not ready" in exc.value.detail.lower()
