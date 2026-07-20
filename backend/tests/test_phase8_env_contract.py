"""Environment-contract coverage for safe Phase 8 deployment defaults."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_checker():
    path = REPO_ROOT / "scripts" / "check_env_contract.py"
    spec = importlib.util.spec_from_file_location("check_env_contract_phase8", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _render_env() -> dict[str, str]:
    return {
        "DATABASE_URL": "postgresql+psycopg2://hidden",
        "REDIS_URL": "redis://hidden",
        "STORAGE_BACKEND": "s3",
        "STORAGE_ROOT": "./data",
        "CV_MAX_UPLOAD_MB": "10",
        "S3_BUCKET": "private-bucket",
        "S3_REGION": "us-east-1",
        "S3_ENDPOINT_URL": "https://s3.example.invalid",
        "S3_PREFIX": "render/cvfit",
        "AWS_USE_IAM_ROLE": "true",
        "JWT_SECRET_KEY": "production-secret-sentinel",
        "CORS_ALLOWED_ORIGINS": "https://frontend.example.invalid",
        "CORS_ALLOW_CREDENTIALS": "false",
        "ENABLE_BILLING": "false",
        "ENABLE_CREDIT_GATING": "false",
        "ENABLE_REALTIME_INTERVIEW": "false",
    }


def test_render_contract_accepts_disabled_realtime_without_openai_key() -> None:
    checker = _load_checker()
    errors, _ = checker.validate("render", _render_env())
    assert errors == []


def test_enabled_realtime_requires_provider_and_bounded_settings() -> None:
    checker = _load_checker()
    values = _render_env()
    values["ENABLE_REALTIME_INTERVIEW"] = "true"
    errors, _ = checker.validate("render", values)
    assert any("OPENAI_API_KEY" in error for error in errors)
    assert any("OPENAI_REALTIME_MODEL" in error for error in errors)
    assert any("OPENAI_REALTIME_CLIENT_SECRET_TTL_SECONDS" in error for error in errors)


def test_enabled_realtime_contract_accepts_complete_server_configuration() -> None:
    checker = _load_checker()
    values = {
        **_render_env(),
        "ENABLE_REALTIME_INTERVIEW": "true",
        "OPENAI_API_KEY": "sk-secret-sentinel",
        "OPENAI_REALTIME_MODEL": "gpt-realtime-test",
        "OPENAI_REALTIME_VOICE": "marin",
        "OPENAI_REALTIME_TRANSCRIPTION_MODEL": "gpt-4o-mini-transcribe",
        "OPENAI_REALTIME_SESSION_MAX_MINUTES": "15",
        "OPENAI_REALTIME_MAX_QUESTIONS": "5",
        "OPENAI_REALTIME_CLIENT_SECRET_TTL_SECONDS": "60",
        "OPENAI_REALTIME_CLIENT_SECRET_MIN_INTERVAL_SECONDS": "30",
    }
    errors, _ = checker.validate("render", values)
    assert errors == []


def test_secret_summary_never_prints_secret_values(capsys) -> None:
    checker = _load_checker()
    values = {
        **_render_env(),
        "OPENAI_API_KEY": "sk-secret-sentinel",
        "PAYOS_CLIENT_ID": "payos-client-sentinel",
        "PAYOS_API_KEY": "payos-secret-sentinel",
    }
    checker.print_present_summary("render", values)
    output = capsys.readouterr().out
    assert "sk-secret-sentinel" not in output
    assert "payos-client-sentinel" not in output
    assert "payos-secret-sentinel" not in output
    assert "OPENAI_API_KEY: set (value hidden)" in output


def test_credit_gating_cannot_enable_without_billing() -> None:
    checker = _load_checker()
    values = _render_env()
    values["ENABLE_CREDIT_GATING"] = "true"
    errors, _ = checker.validate("render", values)
    assert "ENABLE_CREDIT_GATING requires ENABLE_BILLING=true" in errors
