"""Persistence, ownership, and lifecycle rules for realtime interviews."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.db.models import (
    InterviewRealtimeEvent,
    InterviewRealtimeSession,
    InterviewRealtimeTurn,
    User,
)
from app.schemas.interview_realtime import (
    RealtimeEventCreate,
    RealtimeInterviewSessionCreate,
    RealtimeSessionCompleteRequest,
)
from app.services.interview_realtime.context_builder import (
    ContextSources,
    load_owned_context_sources,
)
from app.services.interview_realtime.errors import (
    RealtimeInterviewConflict,
    RealtimeInterviewNotFound,
    RealtimeInterviewValidationError,
)
from app.services.interview_realtime.event_redaction import (
    RedactedRealtimeEvent,
    validate_persistable_text,
)
from app.services.interview_realtime.summary_service import (
    generate_deterministic_summary_if_ready,
    summary_status,
)


ALLOWED_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    "setup": frozenset({"ready", "aborted", "failed"}),
    "ready": frozenset({"active", "completed", "aborted", "failed"}),
    "active": frozenset({"completed", "aborted", "failed"}),
    "completed": frozenset(),
    "aborted": frozenset(),
    "failed": frozenset(),
}

SERVER_EVENT_SESSION_CREATED = "server.session_created"
SERVER_EVENT_SESSION_ACTIVATED = "server.session_activated"
SERVER_EVENT_CLIENT_SECRET_ISSUED = "server.client_secret_issued"
SERVER_EVENT_SESSION_COMPLETED = "server.session_completed"
SERVER_EVENT_SESSION_FAILED = "server.session_failed"
SERVER_EVENT_SUMMARY_GENERATED = "server.summary_generated"
CLIENT_REPORTED_TRANSCRIPT_PROVENANCE = "client_reported_validated"


def create_realtime_session(
    db: Session,
    user: User,
    body: RealtimeInterviewSessionCreate,
    *,
    max_questions: int,
) -> tuple[InterviewRealtimeSession, ContextSources]:
    if body.question_limit > max_questions:
        raise RealtimeInterviewValidationError(
            f"question_limit cannot exceed the server maximum of {max_questions}"
        )
    if body.mode == "realtime_voice" and not body.consent_audio:
        raise RealtimeInterviewValidationError(
            "consent_audio must be true for realtime_voice"
        )
    if body.consent_recording:
        raise RealtimeInterviewValidationError(
            "recording is disabled; this backend does not store audio or video"
        )

    sources = load_owned_context_sources(
        db,
        user.id,
        target_job_id=body.target_job_id,
        application_id=body.application_id,
        analysis_job_id=body.analysis_job_id,
    )
    now = datetime.utcnow()
    session = InterviewRealtimeSession(
        id=uuid.uuid4(),
        user_id=user.id,
        target_job_id=body.target_job_id,
        application_id=body.application_id,
        analysis_job_id=(sources.analysis_job.id if sources.analysis_job else None),
        mode=body.mode,
        status="setup",
        interview_type=body.interview_type,
        difficulty=body.difficulty,
        question_limit=body.question_limit,
        consent_audio=body.consent_audio,
        consent_camera=body.consent_camera,
        consent_recording=body.consent_recording,
        created_at=now,
        updated_at=now,
    )
    transition_session_status(session, "ready", now=now)
    db.add(session)
    db.flush()
    _record_server_lifecycle_event(
        db,
        session,
        SERVER_EVENT_SESSION_CREATED,
        {"status": "ready", "mode": session.mode},
        now=now,
    )
    db.commit()
    db.refresh(session)
    return session, sources


def list_owned_sessions(
    db: Session,
    user_id: uuid.UUID,
    *,
    limit: int,
    offset: int,
) -> tuple[list[InterviewRealtimeSession], int]:
    query = db.query(InterviewRealtimeSession).filter(
        InterviewRealtimeSession.user_id == user_id
    )
    total = query.count()
    items = (
        query.order_by(InterviewRealtimeSession.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return items, total


def get_owned_session(
    db: Session,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
) -> InterviewRealtimeSession:
    session = db.get(InterviewRealtimeSession, session_id)
    if session is None or session.user_id != user_id:
        raise RealtimeInterviewNotFound("realtime interview session not found")
    return session


def transition_session_status(
    session: InterviewRealtimeSession,
    new_status: str,
    *,
    now: datetime | None = None,
    failure_code: str | None = None,
) -> None:
    allowed = ALLOWED_STATUS_TRANSITIONS.get(session.status, frozenset())
    if new_status not in allowed:
        raise RealtimeInterviewConflict(
            f"cannot transition realtime interview from {session.status} to {new_status}"
        )

    timestamp = now or datetime.utcnow()
    session.status = new_status
    session.updated_at = timestamp
    if new_status == "active" and session.started_at is None:
        session.started_at = timestamp
    if new_status in {"completed", "aborted", "failed"}:
        session.ended_at = timestamp
    if new_status == "failed":
        session.failure_code = (failure_code or "realtime_session_failed")[:100]


def prepare_session_for_client_secret(
    db: Session,
    session: InterviewRealtimeSession,
    *,
    max_minutes: int,
    min_interval_seconds: int,
) -> None:
    if not session.consent_audio:
        raise RealtimeInterviewValidationError(
            "audio consent is required before creating a client secret"
        )
    if session.status not in {"ready", "active"}:
        raise RealtimeInterviewConflict(
            f"client secret is unavailable for a {session.status} session"
        )
    _fail_if_expired(db, session, max_minutes=max_minutes)

    issued_events = (
        db.query(InterviewRealtimeEvent)
        .filter(
            InterviewRealtimeEvent.session_id == session.id,
            InterviewRealtimeEvent.event_type == SERVER_EVENT_CLIENT_SECRET_ISSUED,
        )
        .all()
    )
    last_issued_at = max(
        (event.created_at for event in issued_events if event.created_at is not None),
        default=None,
    )
    if (
        last_issued_at is not None
        and datetime.utcnow() < last_issued_at + timedelta(seconds=min_interval_seconds)
    ):
        raise RealtimeInterviewConflict(
            "client secret was issued too recently; retry after the server interval"
        )


def _fail_if_expired(
    db: Session,
    session: InterviewRealtimeSession,
    *,
    max_minutes: int,
) -> None:
    if (
        session.status == "active"
        and session.started_at is not None
        and datetime.utcnow() > session.started_at + timedelta(minutes=max_minutes)
    ):
        transition_session_status(
            session,
            "failed",
            failure_code="session_time_limit_exceeded",
        )
        _record_server_lifecycle_event(
            db,
            session,
            SERVER_EVENT_SESSION_FAILED,
            {"failure_code": "session_time_limit_exceeded"},
        )
        db.commit()
        raise RealtimeInterviewConflict("realtime interview session time limit exceeded")


def mark_session_active(db: Session, session: InterviewRealtimeSession) -> None:
    if session.status == "ready":
        transition_session_status(session, "active")
        _record_server_lifecycle_event(
            db,
            session,
            SERVER_EVENT_SESSION_ACTIVATED,
            {"status": "active"},
        )
    _record_server_lifecycle_event(
        db,
        session,
        SERVER_EVENT_CLIENT_SECRET_ISSUED,
        {"status": session.status},
    )
    db.commit()
    db.refresh(session)


def record_realtime_event(
    db: Session,
    session: InterviewRealtimeSession,
    body: RealtimeEventCreate,
    redacted: RedactedRealtimeEvent,
    *,
    max_minutes: int,
) -> tuple[InterviewRealtimeEvent, bool]:
    if session.status not in {"ready", "active"}:
        raise RealtimeInterviewConflict(
            f"events are unavailable for a {session.status} session"
        )
    _fail_if_expired(db, session, max_minutes=max_minutes)

    sequenced_events = (
        db.query(InterviewRealtimeEvent)
        .filter(InterviewRealtimeEvent.session_id == session.id)
        .all()
    )
    sequenced_events = [
        event for event in sequenced_events if event.event_sequence is not None
    ]
    duplicate = next(
        (
            event
            for event in sequenced_events
            if event.event_sequence == body.event_sequence
        ),
        None,
    )
    if duplicate is not None:
        if (
            duplicate.event_type == body.event_type
            and duplicate.payload_hash == redacted.payload_hash
        ):
            return duplicate, True
        raise RealtimeInterviewConflict(
            "event_sequence conflicts with a previously accepted event"
        )

    expected_sequence = (
        max(event.event_sequence for event in sequenced_events) + 1
        if sequenced_events
        else 0
    )
    if body.event_sequence != expected_sequence:
        raise RealtimeInterviewConflict(
            f"event_sequence must be the next value ({expected_sequence})"
        )

    now = datetime.utcnow()
    if redacted.turn_index is not None:
        _apply_turn_updates(
            db,
            session,
            redacted.turn_index,
            redacted.turn_updates,
            now=now,
        )

    event = InterviewRealtimeEvent(
        id=uuid.uuid4(),
        session_id=session.id,
        event_type=body.event_type,
        event_sequence=body.event_sequence,
        redacted_payload_json=redacted.stored_payload,
        payload_hash=redacted.payload_hash,
        created_at=now,
    )
    db.add(event)
    session.updated_at = now
    db.commit()
    db.refresh(event)
    return event, False


def complete_realtime_session(
    db: Session,
    session: InterviewRealtimeSession,
    body: RealtimeSessionCompleteRequest,
    *,
    max_minutes: int,
) -> tuple[int, str]:
    if session.status == "completed":
        turns = (
            db.query(InterviewRealtimeTurn)
            .filter(InterviewRealtimeTurn.session_id == session.id)
            .all()
        )
        summary = generate_deterministic_summary_if_ready(db, session)
        db.commit()
        return len(turns), summary_status(summary)
    if session.status not in {"ready", "active"}:
        raise RealtimeInterviewConflict(
            f"cannot complete a {session.status} realtime interview session"
        )
    _fail_if_expired(db, session, max_minutes=max_minutes)
    if len(body.turns) > session.question_limit:
        raise RealtimeInterviewValidationError(
            "completed turns cannot exceed the session question limit"
        )

    now = datetime.utcnow()
    for completed_turn in body.turns:
        if completed_turn.turn_index >= session.question_limit:
            raise RealtimeInterviewValidationError(
                "turn_index must be within the session question limit"
            )
        started_at = _utc_naive(completed_turn.started_at)
        ended_at = _utc_naive(completed_turn.ended_at)
        if started_at is not None and ended_at is not None and ended_at < started_at:
            raise RealtimeInterviewValidationError(
                "turn ended_at cannot be earlier than started_at"
            )
        for field_name, value in (
            ("question_text", completed_turn.question_text),
            ("answer_transcript", completed_turn.answer_transcript),
            ("ai_followup_text", completed_turn.ai_followup_text),
        ):
            validate_persistable_text(value, field_name=field_name)

        _apply_turn_updates(
            db,
            session,
            completed_turn.turn_index,
            {
                "question_text": completed_turn.question_text.strip(),
                "question_type": completed_turn.question_type,
                "answer_transcript": (
                    completed_turn.answer_transcript.strip()
                    if completed_turn.answer_transcript
                    else None
                ),
                "ai_followup_text": (
                    completed_turn.ai_followup_text.strip()
                    if completed_turn.ai_followup_text
                    else None
                ),
                "started_at": started_at,
                "ended_at": ended_at,
            },
            now=now,
        )

    transition_session_status(session, "completed", now=now)
    _record_server_lifecycle_event(
        db,
        session,
        SERVER_EVENT_SESSION_COMPLETED,
        {
            "completion_reason": body.completion_reason,
            "completed_turns": len(body.turns),
        },
        now=now,
    )
    db.flush()
    completed_turns = (
        db.query(InterviewRealtimeTurn)
        .filter(InterviewRealtimeTurn.session_id == session.id)
        .count()
    )
    summary = generate_deterministic_summary_if_ready(db, session)
    generated_status = summary_status(summary)
    if generated_status in {"ready", "failed"}:
        _record_server_lifecycle_event(
            db,
            session,
            SERVER_EVENT_SUMMARY_GENERATED,
            {"summary_status": generated_status},
            now=now,
        )
    db.commit()
    db.refresh(session)
    return completed_turns, generated_status


def abort_realtime_session(
    db: Session,
    session: InterviewRealtimeSession,
) -> None:
    transition_session_status(session, "aborted")
    db.commit()


def fail_realtime_session(
    db: Session,
    session: InterviewRealtimeSession,
    *,
    failure_code: str,
) -> None:
    transition_session_status(session, "failed", failure_code=failure_code)
    _record_server_lifecycle_event(
        db,
        session,
        SERVER_EVENT_SESSION_FAILED,
        {"failure_code": failure_code[:100]},
    )
    db.commit()


def _record_server_lifecycle_event(
    db: Session,
    session: InterviewRealtimeSession,
    event_type: str,
    payload: dict[str, object],
    *,
    now: datetime | None = None,
) -> InterviewRealtimeEvent:
    """Persist bounded server-owned lifecycle metadata without transcripts."""
    safe_payload = {
        "source": "server",
        **{
            key: value
            for key, value in payload.items()
            if isinstance(value, (str, int, float, bool)) or value is None
        },
    }
    serialized = json.dumps(
        safe_payload,
        sort_keys=True,
        separators=(",", ":"),
    )
    event = InterviewRealtimeEvent(
        id=uuid.uuid4(),
        session_id=session.id,
        event_type=event_type,
        event_sequence=None,
        redacted_payload_json=safe_payload,
        payload_hash=hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
        created_at=now or datetime.utcnow(),
    )
    db.add(event)
    return event


def _apply_turn_updates(
    db: Session,
    session: InterviewRealtimeSession,
    turn_index: int,
    updates: dict[str, object],
    *,
    now: datetime,
) -> InterviewRealtimeTurn:
    turn = (
        db.query(InterviewRealtimeTurn)
        .filter(
            InterviewRealtimeTurn.session_id == session.id,
            InterviewRealtimeTurn.turn_index == turn_index,
        )
        .one_or_none()
    )
    question_text = updates.get("question_text")
    if turn is None:
        if not isinstance(question_text, str) or not question_text.strip():
            raise RealtimeInterviewValidationError(
                "a question event must be accepted before transcript-only turn events"
            )
        turn = InterviewRealtimeTurn(
            id=uuid.uuid4(),
            session_id=session.id,
            turn_index=turn_index,
            question_text=question_text.strip(),
            created_at=now,
            updated_at=now,
        )
        db.add(turn)

    for field_name in (
        "question_text",
        "question_type",
        "answer_transcript",
        "ai_followup_text",
        "started_at",
        "ended_at",
    ):
        if field_name not in updates:
            continue
        value = updates[field_name]
        if value is None:
            if field_name in {"started_at", "ended_at"}:
                value = now
            else:
                continue
        if isinstance(value, datetime):
            value = _utc_naive(value)
        setattr(turn, field_name, value)
    if any(
        field_name in updates
        for field_name in ("question_text", "answer_transcript", "ai_followup_text")
    ):
        feedback = dict(turn.feedback_json) if isinstance(turn.feedback_json, dict) else {}
        feedback["transcript_provenance"] = CLIENT_REPORTED_TRANSCRIPT_PROVENANCE
        turn.feedback_json = feedback
    turn.updated_at = now
    return turn


def _utc_naive(value: datetime | None) -> datetime | None:
    if value is None or value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)
