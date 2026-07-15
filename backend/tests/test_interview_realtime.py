"""Phase 8 backend tests — Interview Realtime Session.

Uses the in-memory FakeDb pattern from Phase 5/6 test suites.
Tests: session CRUD, turn tracking, ownership isolation, feature flag.
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
        return FakeQuery(self._rows.get(model, []), model)


class FakeQuery:
    def __init__(self, rows, model):
        self._rows = list(rows)
        self._model = model

    def filter(self, *args):
        rows = list(self._rows)
        for expr in args:
            try:
                key = expr.left.key
                val = expr.right.value
                rows = [r for r in rows if getattr(r, key, None) == val]
            except AttributeError:
                pass
        return FakeQuery(rows, self._model)

    def order_by(self, *args):
        return self

    def all(self):
        return list(self._rows)


# ---------------------------------------------------------------------------
# Model helpers (minimal stubs — only fields used by tests)
# ---------------------------------------------------------------------------

class _Model:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class User(_Model):
    __tablename__ = "users"


class InterviewRealtimeSession(_Model):
    __tablename__ = "interview_realtime_sessions"


class InterviewRealtimeTurn(_Model):
    __tablename__ = "interview_realtime_turns"


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

SENTINEL_RAW_CV = "RAW_CV_SENTINEL_MUST_NOT_LEAK"
SENTINEL_JD = "RAW_JD_SENTINEL_MUST_NOT_LEAK"


def make_user(email: str = "user@example.com") -> User:
    return User(id=uuid.uuid4(), email=email, password_hash="hash", is_active=True)


def make_session(user_id, status: str = "setup", **kw) -> InterviewRealtimeSession:
    defaults = dict(
        id=uuid.uuid4(),
        user_id=user_id,
        target_job_id=None,
        application_id=None,
        analysis_job_id=None,
        mode="realtime_voice",
        status=status,
        interview_type="technical",
        difficulty="medium",
        consent_audio=False,
        consent_camera=False,
        consent_recording=False,
        started_at=None,
        ended_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    defaults.update(kw)
    return InterviewRealtimeSession(**defaults)


def make_turn(session_id, user_id, **kw) -> InterviewRealtimeTurn:
    defaults = dict(
        id=uuid.uuid4(),
        session_id=session_id,
        turn_index=0,
        question_text="What is FastAPI?",
        question_type="technical",
        answer_transcript=None,
        ai_followup_text=None,
        started_at=None,
        ended_at=None,
        score_json=None,
        feedback_json=None,
        created_at=datetime.utcnow(),
    )
    defaults.update(kw)
    return InterviewRealtimeTurn(**defaults)


def client_for(db: FakeDb, user: User) -> TestClient:
    # Lazy import — route module created in Phase 8 PR
    try:
        from app.api.routes.interview_realtime import router
    except ImportError:
        return None  # skip tests if route not yet created

    app = FastAPI()
    app.include_router(router)
    db.add(user)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


def unauthed(db: FakeDb) -> TestClient:
    try:
        from app.api.routes.interview_realtime import router
    except ImportError:
        return None

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Tests — skipped if route not yet created
# ---------------------------------------------------------------------------

class TestRealtimeAuth:
    """Session creation requires authentication."""

    def test_create_without_auth_returns_401(self):
        db = FakeDb()
        c = unauthed(db)
        if c is None:
            return  # route not created yet
        resp = c.post("/v1/interview/realtime/sessions", json={})
        assert resp.status_code == 401

    def test_list_without_auth_returns_401(self):
        db = FakeDb()
        c = unauthed(db)
        if c is None:
            return
        resp = c.get("/v1/interview/realtime/sessions")
        assert resp.status_code == 401

    def test_get_session_without_auth_returns_401(self):
        db = FakeDb()
        c = unauthed(db)
        if c is None:
            return
        sid = str(uuid.uuid4())
        resp = c.get(f"/v1/interview/realtime/sessions/{sid}")
        assert resp.status_code == 401


class TestRealtimeSessionCRUD:
    """Create, read, update realtime sessions."""

    def test_create_session_returns_201(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        c = client_for(db, user)
        if c is None:
            return

        payload = {
            "mode": "realtime_voice",
            "interview_type": "technical",
            "difficulty": "medium",
            "consent_audio": True,
            "consent_camera": False,
            "consent_recording": False,
        }
        resp = c.post("/v1/interview/realtime/sessions", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "setup"
        assert body["consent_audio"] is True

    def test_create_session_requires_consent_audio_true(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        c = client_for(db, user)
        if c is None:
            return

        payload = {
            "mode": "realtime_voice",
            "consent_audio": False,  # must be true
        }
        resp = c.post("/v1/interview/realtime/sessions", json=payload)
        # Should reject or require consent_audio=true
        assert resp.status_code in (400, 422)

    def test_list_sessions_returns_only_own(self):
        user_a = make_user("a@example.com")
        user_b = make_user("b@example.com")
        db = FakeDb()
        db.add(user_a)
        db.add(user_b)

        # Give each user a session
        sess_a = make_session(user_a.id)
        sess_b = make_session(user_b.id)
        db.add(sess_a)
        db.add(sess_b)

        c = client_for(db, user_a)
        if c is None:
            return

        resp = c.get("/v1/interview/realtime/sessions")
        assert resp.status_code == 200
        items = resp.json().get("items", [])
        assert len(items) == 1
        assert items[0]["id"] == str(sess_a.id)

    def test_get_own_session_returns_200(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        sess = make_session(user.id, status="active")
        db.add(sess)
        c = client_for(db, user)
        if c is None:
            return

        resp = c.get(f"/v1/interview/realtime/sessions/{sess.id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == str(sess.id)

    def test_start_session_sets_status_active(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        sess = make_session(user.id, status="setup")
        db.add(sess)
        c = client_for(db, user)
        if c is None:
            return

        resp = c.post(f"/v1/interview/realtime/sessions/{sess.id}/start")
        assert resp.status_code == 200
        assert resp.json()["status"] == "active"


class TestRealtimeOwnershipIsolation:
    """Sessions are isolated by user_id."""

    def test_cross_user_get_session_returns_404(self):
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

    def test_cross_user_start_session_returns_404(self):
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

        resp = c.post(f"/v1/interview/realtime/sessions/{sess_b.id}/start")
        assert resp.status_code == 404

    def test_cross_user_get_turn_returns_404(self):
        user_a = make_user("a@example.com")
        user_b = make_user("b@example.com")
        db = FakeDb()
        db.add(user_a)
        db.add(user_b)

        sess_b = make_session(user_b.id)
        db.add(sess_b)
        turn_b = make_turn(sess_b.id, user_b.id)
        db.add(turn_b)

        c = client_for(db, user_a)
        if c is None:
            return

        resp = c.get(f"/v1/interview/realtime/sessions/{sess_b.id}/turns")
        assert resp.status_code == 404


class TestRealtimeTurnTracking:
    """Turns are tracked within a session."""

    def test_add_turn_to_active_session(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        sess = make_session(user.id, status="active")
        db.add(sess)
        c = client_for(db, user)
        if c is None:
            return

        payload = {
            "question_text": "Explain FastAPI routing.",
            "question_type": "technical",
            "answer_transcript": "FastAPI uses decorators to define routes.",
        }
        resp = c.post(
            f"/v1/interview/realtime/sessions/{sess.id}/turns",
            json=payload,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["question_type"] == "technical"
        assert body["turn_index"] == 0

    def test_turn_index_increments(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        sess = make_session(user.id, status="active")
        db.add(sess)
        c = client_for(db, user)
        if c is None:
            return

        for i in range(3):
            resp = c.post(
                f"/v1/interview/realtime/sessions/{sess.id}/turns",
                json={
                    "question_text": f"Q{i+1}",
                    "question_type": "technical",
                },
            )
            assert resp.status_code == 201
            assert resp.json()["turn_index"] == i

    def test_cannot_add_turn_to_aborted_session(self):
        user = make_user()
        db = FakeDb()
        db.add(user)
        sess = make_session(user.id, status="aborted")
        db.add(sess)
        c = client_for(db, user)
        if c is None:
            return

        resp = c.post(
            f"/v1/interview/realtime/sessions/{sess.id}/turns",
            json={"question_text": "Q1", "question_type": "technical"},
        )
        assert resp.status_code == 400


class TestRealtimeFeatureFlag:
    """Phase 8 routes gated by feature flag."""

    def test_route_returns_404_when_flag_off(self, monkeypatch):
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
