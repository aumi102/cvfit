"""Typed API contract for Phase 8 realtime interview backend routes."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


RealtimeInterviewMode = Literal["realtime_voice", "audio_fallback"]
RealtimeInterviewStatus = Literal[
    "setup", "ready", "active", "completed", "aborted", "failed"
]
RealtimeInterviewType = Literal[
    "technical", "behavioral", "project_deep_dive", "hr", "mixed"
]
RealtimeQuestionType = Literal[
    "technical", "behavioral", "project_deep_dive", "hr"
]
RealtimeInterviewDifficulty = Literal["easy", "medium", "hard"]
RealtimeEventType = Literal[
    "session_connected",
    "session_disconnected",
    "question_started",
    "question_completed",
    "user_transcript_completed",
    "assistant_transcript_completed",
    "session_error",
]
RealtimeCompletionReason = Literal["completed", "user_ended", "time_limit"]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RealtimeInterviewSessionCreate(_StrictModel):
    target_job_id: uuid.UUID | None = None
    application_id: uuid.UUID | None = None
    analysis_job_id: uuid.UUID | None = None
    interview_type: RealtimeInterviewType = "mixed"
    difficulty: RealtimeInterviewDifficulty = "medium"
    question_limit: int = Field(default=5, ge=1, le=20)
    mode: RealtimeInterviewMode = "realtime_voice"
    consent_audio: bool = False
    consent_camera: bool = False
    consent_recording: bool = False

    @model_validator(mode="after")
    def validate_context_and_consent(self) -> "RealtimeInterviewSessionCreate":
        if self.mode == "realtime_voice" and not self.consent_audio:
            raise ValueError("consent_audio must be true for realtime_voice")
        if (
            self.target_job_id is not None
            and self.application_id is not None
            and self.target_job_id != self.application_id
        ):
            raise ValueError(
                "target_job_id and application_id must reference the same application when both are set"
            )
        return self


class RealtimeInterviewTurnResponse(_StrictModel):
    id: uuid.UUID
    turn_index: int
    question_text: str
    question_type: str | None = None
    answer_transcript: str | None = None
    ai_followup_text: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    score: dict[str, Any] | None = None
    feedback: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class RealtimeInterviewSessionResponse(_StrictModel):
    id: uuid.UUID
    target_job_id: uuid.UUID | None = None
    application_id: uuid.UUID | None = None
    analysis_job_id: uuid.UUID | None = None
    mode: str
    status: str
    interview_type: str
    difficulty: str
    question_limit: int
    consent_audio: bool
    consent_camera: bool
    consent_recording: bool
    started_at: datetime | None = None
    ended_at: datetime | None = None
    failure_code: str | None = None
    created_at: datetime
    updated_at: datetime
    turn_count: int = 0
    turns: list[RealtimeInterviewTurnResponse] = Field(default_factory=list)


class RealtimeInterviewSessionListResponse(_StrictModel):
    items: list[RealtimeInterviewSessionResponse]
    total: int
    limit: int
    offset: int


class RealtimeClientSecretResponse(_StrictModel):
    interview_session_id: uuid.UUID
    client_secret: str
    expires_at: int
    provider_session_id: str | None = None
    model: str
    voice: str
    configuration_version: str


class RealtimeEventCreate(_StrictModel):
    event_type: RealtimeEventType
    event_sequence: int = Field(ge=0)
    payload: dict[str, Any] = Field(default_factory=dict)


class RealtimeEventResponse(_StrictModel):
    event_id: uuid.UUID
    interview_session_id: uuid.UUID
    event_type: str
    event_sequence: int | None = None
    accepted: bool = True
    replayed: bool = False
    created_at: datetime


class RealtimeCompletedTurn(_StrictModel):
    turn_index: int = Field(ge=0, le=19)
    question_text: str = Field(min_length=1, max_length=4000)
    question_type: RealtimeQuestionType | None = None
    answer_transcript: str | None = Field(default=None, max_length=12000)
    ai_followup_text: str | None = Field(default=None, max_length=4000)
    started_at: datetime | None = None
    ended_at: datetime | None = None


class RealtimeSessionCompleteRequest(_StrictModel):
    turns: list[RealtimeCompletedTurn] = Field(default_factory=list, max_length=20)
    completion_reason: RealtimeCompletionReason = "completed"

    @model_validator(mode="after")
    def validate_unique_turn_indexes(self) -> "RealtimeSessionCompleteRequest":
        indexes = [turn.turn_index for turn in self.turns]
        if len(indexes) != len(set(indexes)):
            raise ValueError("turn_index values must be unique")
        return self


class RealtimeSessionCompleteResponse(_StrictModel):
    interview_session_id: uuid.UUID
    status: str
    completed_turns: int
    summary_status: Literal["ready", "pending", "failed"]
    ended_at: datetime


class RealtimeInterviewSummaryResponse(_StrictModel):
    interview_session_id: uuid.UUID
    status: Literal["ready", "pending", "failed"]
    rubric_version: str | None = None
    overall_score: int | None = None
    rubric: dict[str, Any] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggested_improvements: list[str] = Field(default_factory=list)
    next_practice_questions: list[str] = Field(default_factory=list)
    learning_tasks_to_create: list[dict[str, Any]] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    failure_code: str | None = None
    disclaimer: str = (
        "AI interview feedback is for practice only and does not predict hiring outcomes."
    )
    created_at: datetime | None = None
    updated_at: datetime | None = None
