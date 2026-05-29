"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-05-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    db_url: str = op.get_bind().dialect.name  # type: ignore[reportUnknownMemberType]

    if db_url == "postgresql":
        op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))

        op.execute(
            sa.text(
                "CREATE TYPE job_status AS ENUM "
                "('queued', 'running', 'succeeded', 'failed')"
            )
        )

    # cv_files
    op.create_table(
        "cv_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # jd_docs
    op.create_table(
        "jd_docs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("jd_text", sa.Text(), nullable=False),
        sa.Column("role", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # analysis_jobs
    op.create_table(
        "analysis_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cv_file_id", postgresql.UUID(as_uuid=True),
                   sa.ForeignKey("cv_files.id"), nullable=False),
        sa.Column("jd_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("jd_docs.id"), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM("queued", "running", "succeeded", "failed",
                             name="job_status", create_type=False),
            nullable=False,
            server_default="queued",
        ),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("result_json", postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column("report_docx_path", sa.String(500), nullable=True),
        sa.Column("access_token_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # text_embeddings  (Vector column is PostgreSQL-only)
    if db_url == "postgresql":
        op.create_table(
            "text_embeddings",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("owner_type", sa.String(50), nullable=False),
            sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("text", sa.Text(), nullable=False),
            sa.Column("embedding", postgresql.VECTOR(384), nullable=False),
            sa.Column("meta_json", postgresql.JSONB(astext=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
    else:
        # SQLite fallback — no Vector column, store as JSON
        op.create_table(
            "text_embeddings",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("owner_type", sa.String(50), nullable=False),
            sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("text", sa.Text(), nullable=False),
            sa.Column("embedding", sa.JSON(), nullable=False),
            sa.Column("meta_json", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )

    op.create_index("ix_analysis_jobs_status", "analysis_jobs", ["status"])
    op.create_index("ix_analysis_jobs_created_at", "analysis_jobs", ["created_at"])
    op.create_index("ix_text_embeddings_owner", "text_embeddings",
                    ["owner_type", "owner_id"])


def downgrade() -> None:
    db_url: str = op.get_bind().dialect.name  # type: ignore[reportUnknownMemberType]

    op.drop_index("ix_text_embeddings_owner")
    op.drop_index("ix_analysis_jobs_created_at")
    op.drop_index("ix_analysis_jobs_status")

    op.drop_table("text_embeddings")
    op.drop_table("analysis_jobs")
    op.drop_table("jd_docs")
    op.drop_table("cv_files")

    if db_url == "postgresql":
        op.execute(sa.text("DROP TYPE IF EXISTS job_status"))
