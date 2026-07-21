"""Authenticated Phase 8 realtime interview backend API."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.models import (
    InterviewRealtimeSession,
    InterviewRealtimeSummary,
    InterviewRealtimeTurn,
    User,
)
from app.db.session import get_db
from app.schemas.interview_realtime import (
    RealtimeClientSecretResponse,
    RealtimeEventCreate,
    RealtimeEventResponse,
    RealtimeInterviewSessionCreate,
    RealtimeInterviewSessionListResponse,
    RealtimeInterviewSessionResponse,
    RealtimeInterviewSummaryResponse,
    RealtimeInterviewTurnResponse,
    RealtimeSessionCompleteRequest,
    RealtimeSessionCompleteResponse,
)
from app.services.interview_realtime.context_builder import (
    build_interview_context,
    load_owned_context_sources,
)
from app.services.interview_realtime.errors import (
    RealtimeInterviewConflict,
    RealtimeInterviewNotFound,
    RealtimeInterviewProviderUnavailable,
    RealtimeInterviewUnavailable,
    RealtimeInterviewValidationError,
)
from app.services.interview_realtime.event_redaction import redact_realtime_event
from app.services.interview_realtime.instruction_builder import (
    build_realtime_instructions,
)
from app.services.interview_realtime.realtime_client_service import (
    create_realtime_client_secret,
)
from app.services.interview_realtime.session_service import (
    complete_realtime_session,
    create_realtime_session,
    get_owned_session,
    list_owned_sessions,
    mark_session_active,
    prepare_session_for_client_secret,
    record_realtime_event,
)


def require_realtime_interview_enabled() -> None:
    if not settings.ENABLE_REALTIME_INTERVIEW:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="realtime interview is disabled",
        )


router = APIRouter(
    prefix="/v1/interview/realtime",
    tags=["interview-realtime"],
    dependencies=[Depends(require_realtime_interview_enabled)],
)


@router.post(
    "/sessions",
    response_model=RealtimeInterviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    body: RealtimeInterviewSessionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> RealtimeInterviewSessionResponse:
    try:
        session, _ = create_realtime_session(
            db,
            current_user,
            body,
            max_questions=settings.OPENAI_REALTIME_MAX_QUESTIONS,
        )
    except _DOMAIN_ERRORS as exc:
        _raise_http_error(exc)
    return _session_response(db, session, include_turns=False)


@router.get(
    "/sessions",
    response_model=RealtimeInterviewSessionListResponse,
)
def list_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> RealtimeInterviewSessionListResponse:
    sessions, total = list_owned_sessions(
        db,
        current_user.id,
        limit=limit,
        offset=offset,
    )
    return RealtimeInterviewSessionListResponse(
        items=[
            _session_response(db, session, include_turns=False)
            for session in sessions
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=RealtimeInterviewSessionResponse,
)
def get_session(
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> RealtimeInterviewSessionResponse:
    try:
        session = get_owned_session(db, current_user.id, session_id)
    except _DOMAIN_ERRORS as exc:
        _raise_http_error(exc)
    return _session_response(db, session, include_turns=True)


@router.post(
    "/sessions/{session_id}/client-secret",
    response_model=RealtimeClientSecretResponse,
)
def create_client_secret(
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> RealtimeClientSecretResponse:
    try:
        session = get_owned_session(db, current_user.id, session_id)
        prepare_session_for_client_secret(
            db,
            session,
            max_minutes=settings.OPENAI_REALTIME_SESSION_MAX_MINUTES,
        )
        sources = load_owned_context_sources(
            db,
            current_user.id,
            target_job_id=session.target_job_id,
            application_id=session.application_id,
            analysis_job_id=session.analysis_job_id,
        )
        context = build_interview_context(db, current_user.id, sources)
        instructions = build_realtime_instructions(
            context,
            interview_type=session.interview_type,
            difficulty=session.difficulty,
            question_limit=session.question_limit,
            session_max_minutes=settings.OPENAI_REALTIME_SESSION_MAX_MINUTES,
        )
        credential = create_realtime_client_secret(
            settings,
            user_id=current_user.id,
            instructions=instructions,
        )
        mark_session_active(db, session)
    except _DOMAIN_ERRORS as exc:
        _raise_http_error(exc)

    return RealtimeClientSecretResponse(
        interview_session_id=session.id,
        client_secret=credential.value,
        expires_at=credential.expires_at,
        provider_session_id=credential.provider_session_id,
        model=credential.model,
        voice=credential.voice,
    )


@router.post(
    "/sessions/{session_id}/events",
    response_model=RealtimeEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_event(
    session_id: uuid.UUID,
    body: RealtimeEventCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> RealtimeEventResponse:
    try:
        session = get_owned_session(db, current_user.id, session_id)
        redacted = redact_realtime_event(
            body.event_type,
            body.payload,
            question_limit=session.question_limit,
        )
        event = record_realtime_event(db, session, body, redacted)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="event_sequence has already been accepted",
        )
    except _DOMAIN_ERRORS as exc:
        _raise_http_error(exc)

    return RealtimeEventResponse(
        event_id=event.id,
        interview_session_id=session.id,
        event_type=event.event_type,
        event_sequence=event.event_sequence,
        created_at=event.created_at,
    )


@router.post(
    "/sessions/{session_id}/complete",
    response_model=RealtimeSessionCompleteResponse,
)
def complete_session(
    session_id: uuid.UUID,
    body: RealtimeSessionCompleteRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> RealtimeSessionCompleteResponse:
    try:
        session = get_owned_session(db, current_user.id, session_id)
        completed_turns, summary_ready = complete_realtime_session(
            db,
            session,
            body,
        )
    except _DOMAIN_ERRORS as exc:
        _raise_http_error(exc)

    return RealtimeSessionCompleteResponse(
        interview_session_id=session.id,
        status=session.status,
        completed_turns=completed_turns,
        summary_status="ready" if summary_ready else "pending",
        ended_at=session.ended_at,
    )


@router.get(
    "/sessions/{session_id}/summary",
    response_model=RealtimeInterviewSummaryResponse,
    responses={202: {"model": RealtimeInterviewSummaryResponse}},
)
def get_summary(
    session_id: uuid.UUID,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> RealtimeInterviewSummaryResponse:
    try:
        session = get_owned_session(db, current_user.id, session_id)
    except _DOMAIN_ERRORS as exc:
        _raise_http_error(exc)

    summary = (
        db.query(InterviewRealtimeSummary)
        .filter(InterviewRealtimeSummary.session_id == session.id)
        .one_or_none()
    )
    if summary is None:
        response.status_code = status.HTTP_202_ACCEPTED
        return RealtimeInterviewSummaryResponse(
            interview_session_id=session.id,
            status="pending",
            limitations=[
                "Summary is not ready. Completed turns are persisted, but no trusted rubric evaluation is available yet."
            ],
        )

    return RealtimeInterviewSummaryResponse(
        interview_session_id=session.id,
        status="ready",
        overall_score=summary.overall_score,
        rubric=summary.rubric_json or {},
        strengths=summary.strengths_json or [],
        weaknesses=summary.weaknesses_json or [],
        suggested_improvements=summary.suggested_improvements_json or [],
        next_practice_questions=summary.next_questions_json or [],
        learning_tasks_to_create=summary.learning_tasks_json or [],
        limitations=summary.limitations_json or [],
        created_at=summary.created_at,
        updated_at=summary.updated_at,
    )


def _session_response(
    db: Session,
    session: InterviewRealtimeSession,
    *,
    include_turns: bool,
) -> RealtimeInterviewSessionResponse:
    query = db.query(InterviewRealtimeTurn).filter(
        InterviewRealtimeTurn.session_id == session.id
    )
    turn_count = query.count()
    turns = query.order_by(InterviewRealtimeTurn.turn_index.asc()).all() if include_turns else []
    return RealtimeInterviewSessionResponse(
        id=session.id,
        target_job_id=session.target_job_id,
        application_id=session.application_id,
        analysis_job_id=session.analysis_job_id,
        mode=session.mode,
        status=session.status,
        interview_type=session.interview_type,
        difficulty=session.difficulty,
        question_limit=session.question_limit,
        consent_audio=session.consent_audio,
        consent_camera=session.consent_camera,
        consent_recording=session.consent_recording,
        started_at=session.started_at,
        ended_at=session.ended_at,
        failure_code=session.failure_code,
        created_at=session.created_at,
        updated_at=session.updated_at,
        turn_count=turn_count,
        turns=[_turn_response(turn) for turn in turns],
    )


def _turn_response(turn: InterviewRealtimeTurn) -> RealtimeInterviewTurnResponse:
    return RealtimeInterviewTurnResponse(
        id=turn.id,
        turn_index=turn.turn_index,
        question_text=turn.question_text,
        question_type=turn.question_type,
        answer_transcript=turn.answer_transcript,
        ai_followup_text=turn.ai_followup_text,
        started_at=turn.started_at,
        ended_at=turn.ended_at,
        score=turn.score_json,
        feedback=turn.feedback_json,
        created_at=turn.created_at,
        updated_at=turn.updated_at,
    )


_DOMAIN_ERRORS = (
    RealtimeInterviewNotFound,
    RealtimeInterviewValidationError,
    RealtimeInterviewConflict,
    RealtimeInterviewUnavailable,
    RealtimeInterviewProviderUnavailable,
)


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, RealtimeInterviewNotFound):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, RealtimeInterviewValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, RealtimeInterviewConflict):
        status_code = status.HTTP_409_CONFLICT
    else:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    raise HTTPException(status_code=status_code, detail=str(exc))
