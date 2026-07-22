from app.api.routes.health import health
from app.core.build_metadata import safe_build_metadata


def test_build_metadata_is_allowlisted_and_rejects_invalid_values() -> None:
    metadata = safe_build_metadata(
        "worker",
        {
            "RENDER_GIT_COMMIT": "1099396339a24e9b3d1387301a2c57f397f1bb55",
            "APP_ENVIRONMENT": "production",
            "BUILD_TIME": "2026-07-22T08:30:00Z",
            "OPENAI_API_KEY": "must-not-leak",
            "DATABASE_URL": "must-not-leak",
        },
    )

    assert metadata == {
        "service": "worker",
        "commit_sha": "1099396339a24e9b3d1387301a2c57f397f1bb55",
        "environment": "production",
        "build_time": "2026-07-22T08:30:00Z",
    }
    assert "must-not-leak" not in str(metadata)
    assert safe_build_metadata(
        "backend",
        {"RENDER_GIT_COMMIT": "not-a-sha", "BUILD_TIME": "not-a-time"},
    ) == {
        "service": "backend",
        "commit_sha": "unknown",
        "environment": "unknown",
        "build_time": None,
    }


def test_health_includes_safe_backend_version_fields(monkeypatch) -> None:
    monkeypatch.setenv("RENDER_GIT_COMMIT", "1099396")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-leak")

    payload = health()

    assert payload["status"] == "ok"
    assert payload["service"] == "backend"
    assert payload["commit_sha"] == "1099396"
    assert "must-not-leak" not in str(payload)
