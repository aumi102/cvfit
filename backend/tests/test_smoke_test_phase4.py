import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import smoke_test_phase4


def valid_v3_result_payload():
    return {
        "job_id": "job-1",
        "overall_fit_score": 81,
        "result": {
            "schema_version": "3.0",
            "fit_score": 81,
            "scores": {"fit_score": 81},
            "overall": {"fit_score": 81},
            "improvement_actions": [],
            "safe_rewrite_suggestions": [],
            "interview_prep": [],
            "learning_roadmap": [],
            "limitations": [],
        },
    }


def valid_comparison_payload():
    return {
        "base_job_id": "base",
        "new_job_id": "new",
        "base_score": 70,
        "new_score": 82,
        "score_delta": 12,
        "breakdown_delta": {"skill_match": 10},
        "resolved_missing_skills": [],
        "still_missing_skills": [],
        "newly_matched_skills": [],
        "new_evidence": [],
        "keyword_stuffing_warnings": [],
        "improvement_summary": "The revised CV score improved by 12 points.",
        "next_actions": [],
    }


def test_redact_text_hides_tokens_and_token_bearing_urls():
    text = smoke_test_phase4.redact_text(
        'GET https://example.test/path?access_token=secret-token '
        'Authorization: Bearer jwt-token {"access_token": "json-token"} '
        "form access_token=form-token&next=1 JWT=jwt-like-token"
    )

    assert "secret-token" not in text
    assert "jwt-token" not in text
    assert "json-token" not in text
    assert "form-token" not in text
    assert "jwt-like-token" not in text
    assert "access_token=<hidden>" in text or "<redacted-url>" in text


def test_mutating_mode_refuses_without_explicit_flag(monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "https://cvfit.example.test")
    monkeypatch.delenv("SMOKE_ALLOW_MUTATING", raising=False)

    assert smoke_test_phase4.main(["--mutating"]) == 1


def test_validate_result_v3_payload_accepts_required_shape():
    schema_version, fit_score = smoke_test_phase4.validate_result_v3_payload(
        valid_v3_result_payload()
    )

    assert schema_version == "3.0"
    assert fit_score == 81


def test_validate_result_v3_payload_catches_missing_v3_fields():
    payload = valid_v3_result_payload()
    del payload["result"]["learning_roadmap"]

    try:
        smoke_test_phase4.validate_result_v3_payload(payload)
    except smoke_test_phase4.SmokeError as exc:
        assert "learning_roadmap" in str(exc)
    else:
        raise AssertionError("expected missing v3 field to fail")


def test_validate_comparison_payload_accepts_required_shape():
    assert smoke_test_phase4.validate_comparison_payload(valid_comparison_payload()) == 12


def test_validate_comparison_payload_catches_missing_required_key():
    payload = valid_comparison_payload()
    del payload["next_actions"]

    try:
        smoke_test_phase4.validate_comparison_payload(payload)
    except smoke_test_phase4.SmokeError as exc:
        assert "next_actions" in str(exc)
    else:
        raise AssertionError("expected missing comparison key to fail")


def test_validate_comparison_payload_catches_sensitive_terms():
    payload = valid_comparison_payload()
    payload["new_evidence"] = [{"storage_path": "uploads/private.docx"}]

    try:
        smoke_test_phase4.validate_comparison_payload(payload)
    except smoke_test_phase4.SmokeError as exc:
        assert "storage_path" in str(exc)
    else:
        raise AssertionError("expected sensitive comparison field to fail")


def test_read_only_mode_does_not_read_database_url(monkeypatch, capsys):
    called = []

    def fake_request_json(base_url, method, path, body=None, timeout=30):
        called.append((base_url, method, path))
        return {"status": "ok"}

    monkeypatch.setenv("API_BASE_URL", "https://cvfit.example.test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://should-not-be-used")
    monkeypatch.setattr(smoke_test_phase4, "request_json", fake_request_json)

    assert smoke_test_phase4.main([]) == 0
    assert called == [("https://cvfit.example.test", "GET", "/health")]
    assert "DATABASE_URL" not in capsys.readouterr().out


def test_minimal_docx_writer_can_be_read_with_stdlib(tmp_path):
    path = tmp_path / "smoke.docx"

    smoke_test_phase4.write_minimal_docx(path, ["Hello", "Phase 4"])
    text = smoke_test_phase4.extract_docx_text_stdlib(path.read_bytes())

    assert text is not None
    assert "Hello" in text
    assert "Phase 4" in text
