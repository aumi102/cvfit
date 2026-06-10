"""Add applications and career_profile_items tables.

Revision ID: 20260610_0001
Revises: 20260606_0001
Create Date: 2026-06-10
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260610_0001"
down_revision = "20260606_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("job_title", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("jd_text", sa.Text, nullable=False),
        sa.Column("target_role", sa.String(255), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "analyzing",
                "improving_cv",
                "ready_to_apply",
                "interview_prep",
                "applied",
                "archived",
                name="application_status",
            ),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("best_analysis_job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analysis_jobs.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_applications_user_id", "applications", ["user_id"], unique=False)
    op.create_index("ix_applications_status", "applications", ["status"], unique=False)
    op.create_index("ix_applications_best_analysis_job_id", "applications", ["best_analysis_job_id"], unique=False)

    op.create_table(
        "career_profile_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "item_type",
            sa.Enum(
                "skill",
                "project",
                "experience",
                "education",
                "certification",
                "achievement",
                "link",
                name="career_profile_item_type",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("skills_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("evidence_text", sa.Text, nullable=True),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_career_profile_items_user_id", "career_profile_items", ["user_id"], unique=False)
    op.create_index("ix_career_profile_items_item_type", "career_profile_items", ["item_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_career_profile_items_item_type", table_name="career_profile_items")
    op.drop_index("ix_career_profile_items_user_id", table_name="career_profile_items")
    op.drop_table("career_profile_items")
    op.execute("DROP TYPE IF EXISTS career_profile_item_type")

    op.drop_index("ix_applications_best_analysis_job_id", table_name="applications")
    op.drop_index("ix_applications_status", table_name="applications")
    op.drop_index("ix_applications_user_id", table_name="applications")
    op.drop_table("applications")
    op.execute("DROP TYPE IF EXISTS application_status")
