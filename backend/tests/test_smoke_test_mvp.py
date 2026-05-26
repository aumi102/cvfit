import os
import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import smoke_test_mvp


def test_read_only_mode_requires_api_base_url(monkeypatch):
    monkeypatch.delenv("API_BASE_URL", raising=False)

    assert smoke_test_mvp.main([]) == 1


def test_mutating_mode_refuses_without_explicit_flag(monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "https://cvfit.example.test")
    monkeypatch.delenv("SMOKE_ALLOW_MUTATING", raising=False)

    assert smoke_test_mvp.main(["--mutating"]) == 1


def test_normalize_base_url_strips_trailing_slashes():
    assert smoke_test_mvp.normalize_base_url(" https://cvfit.example.test/// ") == (
        "https://cvfit.example.test"
    )


def test_configured_timeout_rejects_invalid_values(monkeypatch):
    monkeypatch.setenv("SMOKE_TIMEOUT_SECONDS", "not-a-number")

    try:
        smoke_test_mvp.configured_timeout()
    except smoke_test_mvp.SmokeError as exc:
        assert "SMOKE_TIMEOUT_SECONDS" in str(exc)
    else:
        raise AssertionError("expected invalid timeout to raise SmokeError")


def test_smoke_allow_mutating_must_equal_one(monkeypatch):
    monkeypatch.setenv("SMOKE_ALLOW_MUTATING", "true")

    assert not smoke_test_mvp.env_flag_enabled("SMOKE_ALLOW_MUTATING")


def test_redact_url_hides_access_token():
    redacted = smoke_test_mvp.redact_url(
        "/v1/jobs/job-1/report/download?access_token=secret-token"
    )

    assert redacted == "/v1/jobs/job-1/report/download?access_token=<hidden>"
    assert "secret-token" not in redacted


def test_read_only_mode_does_not_read_database_url(monkeypatch, capsys):
    called_paths = []

    def fake_request_json(base_url, method, path, body=None, timeout=30):
        called_paths.append((base_url, method, path))
        return {"status": "ok"}

    monkeypatch.setenv("API_BASE_URL", "https://cvfit.example.test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://should-not-be-used")
    monkeypatch.setattr(smoke_test_mvp, "request_json", fake_request_json)

    assert smoke_test_mvp.main([]) == 0
    assert called_paths == [("https://cvfit.example.test", "GET", "/health")]
    assert "DATABASE_URL" not in capsys.readouterr().out


def test_mutating_mode_polls_until_success(monkeypatch, tmp_path):
    created_docx = tmp_path / "synthetic.docx"
    created_docx.write_bytes(b"fake-docx")
    calls = []
    statuses = iter(
        [
            {"job_id": "job-1", "status": "queued", "progress": 0},
            {"job_id": "job-1", "status": "succeeded", "progress": 100},
        ]
    )

    def fake_request_json(base_url, method, path, body=None, timeout=30):
        calls.append((method, path))
        if path == "/health":
            return {"status": "ok"}
        if path == "/v1/jobs/create-score":
            return {"job_id": "job-1", "access_token": "secret-token"}
        if path == "/v1/jobs/job-1":
            return next(statuses)
        if path.startswith("/v1/jobs/job-1/result?"):
            return {"job_id": "job-1", "result": {"scores": {"fit_score": 88}}}
        if path.startswith("/v1/jobs/job-1/report?"):
            return {"format": "docx", "download_url": "/v1/jobs/job-1/report/download?access_token=secret-token"}
        raise AssertionError(f"unexpected JSON request: {method} {path}")

    def fake_post_multipart_file(base_url, path, field_name, file_path, content_type):
        calls.append(("POST", path))
        assert file_path == created_docx
        return {"cv_file_id": "cv-1"}

    def fake_request_bytes(base_url, method, path, timeout=60):
        calls.append((method, path))
        return b"x" * 1001

    monkeypatch.setenv("API_BASE_URL", "https://cvfit.example.test")
    monkeypatch.setenv("SMOKE_ALLOW_MUTATING", "1")
    monkeypatch.setattr(smoke_test_mvp, "create_synthetic_docx_cv", lambda: created_docx)
    monkeypatch.setattr(smoke_test_mvp, "request_json", fake_request_json)
    monkeypatch.setattr(smoke_test_mvp, "post_multipart_file", fake_post_multipart_file)
    monkeypatch.setattr(smoke_test_mvp, "request_bytes", fake_request_bytes)
    monkeypatch.setattr(smoke_test_mvp.time, "sleep", lambda seconds: None)

    assert smoke_test_mvp.main(["--mutating"]) == 0
    assert ("POST", "/v1/cv/upload") in calls
    assert ("POST", "/v1/jobs/create-score") in calls
    assert ("GET", "/v1/jobs/job-1") in calls
    assert (
        "GET",
        "/v1/jobs/job-1/report/download?access_token=secret-token",
    ) in calls
    assert not created_docx.exists()
