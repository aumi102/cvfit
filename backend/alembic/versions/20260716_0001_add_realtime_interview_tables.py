"""Add Phase 8 realtime interview backend tables.

The migration is additive and leaves the existing typed-answer and Interview
Practice v2 tables unchanged. Realtime provider secrets, SDP, and media are not
represented in this schema.

Revision ID: 20260716_0001
Revises: 20260623_0001
Create Date: 2026-07-16
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260716_0001"
down_revision = "20260623_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "interview_realtime_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("analysis_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("mode", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="setup", nullable=False),
        sa.Column("interview_type", sa.String(length=30), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("question_limit", sa.Integer(), nullable=False),
        sa.Column("consent_audio", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("consent_camera", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("consent_recording", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("failure_code", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["target_job_id"], ["applications.id"]),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.ForeignKeyConstraint(["analysis_job_id"], ["analysis_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_interview_realtime_sessions_user_id",
        "interview_realtime_sessions",
        ["user_id"],
    )
    op.create_index(
        "ix_interview_realtime_sessions_target_job_id",
        "interview_realtime_sessions",
        ["target_job_id"],
    )
    op.create_index(
        "ix_interview_realtime_sessions_application_id",
        "interview_realtime_sessions",
        ["application_id"],
    )
    op.create_index(
        "ix_interview_realtime_sessions_analysis_job_id",
        "interview_realtime_sessions",
        ["analysis_job_id"],
    )
    op.create_index(
        "ix_interview_realtime_sessions_status",
        "interview_realtime_sessions",
        ["status"],
    )
    op.create_index(
        "ix_interview_realtime_sessions_created_at",
        "interview_realtime_sessions",
        ["created_at"],
    )

    op.create_table(
        "interview_realtime_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=30), nullable=True),
        sa.Column("answer_transcript", sa.Text(), nullable=True),
        sa.Column("ai_followup_text", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("score_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("feedback_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["interview_realtime_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "session_id",
            "turn_index",
            name="uq_interview_realtime_turns_session_turn",
        ),
    )
    op.create_index(
        "ix_interview_realtime_turns_session_id",
        "interview_realtime_turns",
        ["session_id"],
    )

    op.create_table(
        "interview_realtime_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_sequence", sa.Integer(), nullable=True),
        sa.Column(
            "redacted_payload_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("payload_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["interview_realtime_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "session_id",
            "event_sequence",
            name="uq_interview_realtime_events_session_sequence",
        ),
    )
    op.create_index(
        "ix_interview_realtime_events_session_id",
        "interview_realtime_events",
        ["session_id"],
    )
    op.create_index(
        "ix_interview_realtime_events_event_type",
        "interview_realtime_events",
        ["event_type"],
    )
    op.create_index(
        "ix_interview_realtime_events_created_at",
        "interview_realtime_events",
        ["created_at"],
    )

    op.create_table(
        "interview_realtime_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=True),
        sa.Column("rubric_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("strengths_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("weaknesses_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "suggested_improvements_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("next_questions_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("learning_tasks_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("limitations_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["interview_realtime_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_interview_realtime_summaries_session_id",
        "interview_realtime_summaries",
        ["session_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_interview_realtime_summaries_session_id",
        table_name="interview_realtime_summaries",
    )
    op.drop_table("interview_realtime_summaries")

    op.drop_index(
        "ix_interview_realtime_events_created_at",
        table_name="interview_realtime_events",
    )
    op.drop_index(
        "ix_interview_realtime_events_event_type",
        table_name="interview_realtime_events",
    )
    op.drop_index(
        "ix_interview_realtime_events_session_id",
        table_name="interview_realtime_events",
    )
    op.drop_table("interview_realtime_events")

    op.drop_index(
        "ix_interview_realtime_turns_session_id",
        table_name="interview_realtime_turns",
    )
    op.drop_table("interview_realtime_turns")

    op.drop_index(
        "ix_interview_realtime_sessions_created_at",
        table_name="interview_realtime_sessions",
    )
    op.drop_index(
        "ix_interview_realtime_sessions_status",
        table_name="interview_realtime_sessions",
    )
    op.drop_index(
        "ix_interview_realtime_sessions_analysis_job_id",
        table_name="interview_realtime_sessions",
    )
    op.drop_index(
        "ix_interview_realtime_sessions_application_id",
        table_name="interview_realtime_sessions",
    )
    op.drop_index(
        "ix_interview_realtime_sessions_target_job_id",
        table_name="interview_realtime_sessions",
    )
    op.drop_index(
        "ix_interview_realtime_sessions_user_id",
        table_name="interview_realtime_sessions",
    )
    op.drop_table("interview_realtime_sessions")
