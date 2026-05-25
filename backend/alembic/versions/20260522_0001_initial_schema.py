"""Initial schema baseline.

Revision ID: 20260522_0001
Revises:
Create Date: 2026-05-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


revision = "20260522_0001"
down_revision = None
branch_labels = None
depends_on = None


def _embedding_type():
    if Vector is None:
        return postgresql.JSONB(astext_type=sa.Text())
    return Vector(384)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    job_status = postgresql.ENUM(
        "queued",
        "running",
        "succeeded",
        "failed",
        name="job_status",
        create_type=False,
    )
    postgresql.ENUM(
        "queued",
        "running",
        "succeeded",
        "failed",
        name="job_status",
    ).create(op.get_bind(), checkfirst=True)

    op.create_table(
        "cv_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "jd_docs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("jd_text", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "analysis_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cv_file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("jd_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("report_docx_path", sa.String(length=500), nullable=True),
        sa.Column("access_token_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["cv_file_id"], ["cv_files.id"]),
        sa.ForeignKeyConstraint(["jd_id"], ["jd_docs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "text_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_type", sa.String(length=50), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", _embedding_type(), nullable=False),
        sa.Column("meta_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("text_embeddings")
    op.drop_table("analysis_jobs")
    op.drop_table("jd_docs")
    op.drop_table("cv_files")
    sa.Enum(name="job_status").drop(op.get_bind(), checkfirst=True)
