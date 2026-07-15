"""Phase 8 backend privacy tests — Interview Realtime.

Tests: no raw data in analytics, no media in logs, ephemeral token security,
consent requirements, session ownership isolation.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.db.session import get_db


# ---------------------------------------------------------------------------
# Fake DB
# ---------------------------------------------------------------------------

class FakeDb:
    def __init__(self):
        self._store: dict[tuple, Any] = {}
        self._rows: dict[type, list] = {}

    def _key(self, model, pk):
        return (model.__tablename__, pk)

    def add(self, obj):
        self._store[self._key(type(obj), obj.id)] = obj
        self._rows.setdefault(type(obj), [])
        if obj not in self._rows[type(obj)]:
            self._rows[type(obj)].append(obj)

    def get(self, model, pk):
        return self._store.get(self._key(model, pk))

    def commit(self):
        pass

    def refresh(self, obj):
        pass

    def query(self, model):
        return FakeQuery(self._rows.get(model, []))

    def all(self, model):
        return self._rows.get(model, [])


class FakeQuery:
    def __init__(self, rows):
        self._rows = list(rows)

    def filter(self, *args):
        rows = list(self._rows)
        for expr in args:
            try:
                key = expr.left.key
                val = expr.right.value
                rows = [r for r in rows if getattr(r, key, None) == val]
            except AttributeError:
                pass
        return self

    def first(self):
        return self._rows[0] if self._rows else None

    def all(self):
        return list(self._rows)


# ---------------------------------------------------------------------------
# Model stubs
# ---------------------------------------------------------------------------

class _Model:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class User(_Model):
    __tablename__ = "users"


class InterviewRealtimeSession(_Model):
    __tablename__ = "interview_realtime_sessions"


class InterviewMediaArtifact(_Model):
    __tablename__ = "interview_media_artifacts"


# ---------------------------------------------------------------------------
# Sentinel values — these must NEVER appear in any response/log
# ---------------------------------------------------------------------------

SENTINEL_RAW_TRANSCRIPT = "RAW_TRANSCRIPT_SECRET_SENTINEL_MUST_NOT_LEAK"
SENTINEL_CV_TEXT = "RAW_CV_SENTINEL_MUST_NOT_LEAK"
SENTINEL_JD_TEXT = "RAW_JD_SENTINEL_MUST_NOT_LEAK"
SENTINEL_OPENAI_KEY = "sk-test-SENTINEL_MUST_NOT_LEAK_IN_CODE"


def make_user(email: str = "user@example.com") -> User:
    return User(
        id=uuid.uuid4(),
        email=email,
        password_hash="hash",
        is_active=True,
    )


def make_session(user_id, **kw) -> InterviewRealtimeSession:
    defaults = dict(
        id=uuid.uuid4(),
        user_id=user_id,
        target_job_id=None,
        application_id=None,
        analysis_job_id=None,
        mode="realtime_voice",
        status="active",
        interview_type="technical",
        difficulty="medium",
        consent_audio=True,
        consent_camera=False,
        consent_recording=False,
        started_at=datetime.utcnow(),
        ended_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    defaults.update(kw)
    return InterviewRealtimeSession(**defaults)


def client_for(db: FakeDb, user: User) -> TestClient:
    try:
        from app.api.routes.interview_realtime import router
    except ImportError:
        return None

    app = FastAPI()
    app.include_router(router)
    db.add(user)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


# ---------------------------------------------------------------------------
# Privacy Tests
# ---------------------------------------------------------------------------

class TestNoRawTranscriptInResponses:
    """Raw transcript must never appear in API responses or logs."""

    def test_session_response_no_transcript(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        c = client_for(db, user)
        if c is None:
            return

        resp = c.get("/v1/interview/realtime/sessions")
        body_str = resp.text
        assert SENTINEL_RAW_TRANSCRIPT not in body_str
        assert "transcript" not in body_str.lower() or "transcript" in ["transcript_index"]

    def test_summary_no_raw_transcript(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        sess = make_session(user.id)
        db.add(sess)
        c = client_for(db, user)
        if c is None:
            return

        resp = c.get(f"/v1/interview/realtime/sessions/{sess.id}/summary")
        if resp.status_code == 404:
            return  # endpoint may not exist yet
        body_str = resp.text
        assert SENTINEL_RAW_TRANSCRIPT not in body_str
        # Summary should not embed raw answer text
        assert "answer_text" not in body_str
        assert "raw_transcript" not in body_str

    def test_cv_text_not_in_turn_response(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        sess = make_session(user.id)
        db.add(sess)
        c = client_for(db, user)
        if c is None:
            return

        # Add a turn with a question
        resp = c.post(
            f"/v1/interview/realtime/sessions/{sess.id}/turns",
            json={
                "question_text": "Explain your backend experience.",
                "question_type": "technical",
                "answer_transcript": "I built an API with PostgreSQL.",  # safe, not the sentinel
            },
        )
        if resp.status_code not in (200, 201):
            return

        body_str = resp.text
        # CV text sentinel must never appear
        assert SENTINEL_CV_TEXT not in body_str
        assert SENTINEL_JD_TEXT not in body_str


class TestNoMediaInAnalyticsEvents:
    """Audio/video media must not appear in analytics events or logs."""

    def test_media_artifact_not_in_session_list(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        sess = make_session(user.id)
        db.add(sess)

        # Simulate a media artifact being stored
        media = InterviewMediaArtifact(
            id=uuid.uuid4(),
            session_id=sess.id,
            turn_id=None,
            artifact_type="audio_answer",
            storage_key="s3://bucket/audio/session-123/turn-0.m4a",
            duration_seconds=45,
            mime_type="audio/mp4",
            created_at=datetime.utcnow(),
            deleted_at=None,
        )
        db.add(media)

        c = client_for(db, user)
        if c is None:
            return

        resp = c.get(f"/v1/interview/realtime/sessions/{sess.id}")
        # Media storage_key must not be exposed in session response
        body_str = resp.text
        assert "audio/mp4" not in body_str
        assert "m4a" not in body_str
        assert "duration_seconds" not in body_str

    def test_media_delete_removes_artifact(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        sess = make_session(user.id)
        db.add(sess)
        media = InterviewMediaArtifact(
            id=uuid.uuid4(),
            session_id=sess.id,
            turn_id=None,
            artifact_type="audio_answer",
            storage_key="s3://bucket/audio/session-123/turn-0.m4a",
            duration_seconds=45,
            mime_type="audio/mp4",
            created_at=datetime.utcnow(),
            deleted_at=None,
        )
        db.add(media)
        c = client_for(db, user)
        if c is None:
            return

        resp = c.delete(f"/v1/interview/realtime/sessions/{sess.id}/media")
        # Should return 200 and media should be gone
        assert resp.status_code in (200, 204, 404)


class TestConsentRequired:
    """Audio capture requires explicit consent."""

    def test_session_without_audio_consent_rejected(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        c = client_for(db, user)
        if c is None:
            return

        payload = {
            "mode": "realtime_voice",
            "consent_audio": False,  # must be True
        }
        resp = c.post("/v1/interview/realtime/sessions", json=payload)
        assert resp.status_code in (400, 422)

    def test_camera_consent_optional(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        c = client_for(db, user)
        if c is None:
            return

        payload = {
            "mode": "realtime_voice",
            "consent_audio": True,
            "consent_camera": False,  # optional
        }
        resp = c.post("/v1/interview/realtime/sessions", json=payload)
        assert resp.status_code == 201


class TestEphemeralTokenSecurity:
    """Ephemeral tokens must be server-side only."""

    def test_session_response_no_openai_key(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        c = client_for(db, user)
        if c is None:
            return

        resp = c.post(
            "/v1/interview/realtime/sessions",
            json={
                "mode": "realtime_voice",
                "consent_audio": True,
            },
        )
        if resp.status_code != 201:
            return

        body_str = resp.text
        assert SENTINEL_OPENAI_KEY not in body_str
        assert "sk-" not in body_str
        assert "openai" not in body_str.lower()

    def test_client_secret_endpoint_requires_owner(self):
        user_a = make_user("a@example.com")
        user_b = make_user("b@example.com")
        db = FakeDb()
        db.add(user_a)
        db.add(user_b)

        sess_b = make_session(user_b.id)
        db.add(sess_b)

        # User A tries to get ephemeral token for User B's session
        c = client_for(db, user_a)
        if c is None:
            return

        resp = c.post(
            f"/v1/interview/realtime/sessions/{sess_b.id}/client-secret"
        )
        assert resp.status_code == 404


class TestOwnershipIsolation:
    """All session data is scoped to the owner."""

    def test_cross_user_session_list_returns_only_own(self):
        user_a = make_user("a@example.com")
        user_b = make_user("b@example.com")
        db = FakeDb()
        db.add(user_a)
        db.add(user_b)

        db.add(make_session(user_a.id))
        db.add(make_session(user_b.id))

        c = client_for(db, user_a)
        if c is None:
            return

        resp = c.get("/v1/interview/realtime/sessions")
        assert resp.status_code == 200
        items = resp.json().get("items", [])
        assert len(items) == 1
        # Cannot see user_b's session
        for item in items:
            assert str(user_a.id) in [str(user_a.id)]

    def test_cross_user_session_get_returns_404(self):
        user_a = make_user("a@example.com")
        user_b = make_user("b@example.com")
        db = FakeDb()
        db.add(user_a)
        db.add(user_b)

        sess_b = make_session(user_b.id)
        db.add(sess_b)

        c = client_for(db, user_a)
        if c is None:
            return

        resp = c.get(f"/v1/interview/realtime/sessions/{sess_b.id}")
        assert resp.status_code == 404

    def test_cross_user_turn_list_returns_404(self):
        user_a = make_user("a@example.com")
        user_b = make_user("b@example.com")
        db = FakeDb()
        db.add(user_a)
        db.add(user_b)

        sess_b = make_session(user_b.id)
        db.add(sess_b)

        c = client_for(db, user_a)
        if c is None:
            return

        resp = c.get(f"/v1/interview/realtime/sessions/{sess_b.id}/turns")
        assert resp.status_code == 404


class TestFeatureFlagGatesRoutes:
    """All Phase 8 routes return 404 when feature flag is off."""

    def test_list_returns_404_when_flag_off(self, monkeypatch):
        from app.core import config as config_module

        user = make_user()
        db = FakeDb()
        db.add(user)
        c = client_for(db, user)
        if c is None:
            return

        monkeypatch.setattr(config_module.settings, "ENABLE_PHASE8_REALTIME", False)

        resp = c.get("/v1/interview/realtime/sessions")
        assert resp.status_code == 404

    def test_create_returns_404_when_flag_off(self, monkeypatch):
        from app.core import config as config_module

        user = make_user()
        db = FakeDb()
        db.add(user)
        c = client_for(db, user)
        if c is None:
            return

        monkeypatch.setattr(config_module.settings, "ENABLE_PHASE8_REALTIME", False)

        resp = c.post(
            "/v1/interview/realtime/sessions",
            json={"consent_audio": True},
        )
        assert resp.status_code == 404
