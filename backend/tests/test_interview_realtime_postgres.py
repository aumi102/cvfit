"""Phase 8 migration contract, including disposable PostgreSQL validation."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

from app.db import init_db


BACKEND_ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (
    BACKEND_ROOT
    / "alembic"
    / "versions"
    / "20260716_0001_add_realtime_interview_tables.py"
)
PHASE8_TABLES = {
    "interview_realtime_sessions",
    "interview_realtime_turns",
    "interview_realtime_events",
    "interview_realtime_summaries",
}


def test_phase8_migration_is_linear_and_runtime_head_matches() -> None:
    text = MIGRATION.read_text(encoding="utf-8")
    assert 'revision = "20260716_0001"' in text
    assert 'down_revision = "20260623_0001"' in text
    assert init_db.EXPECTED_ALEMBIC_HEAD == "20260716_0001"
    for table in PHASE8_TABLES:
        assert f'"{table}"' in text
    assert "interview_media_artifacts" not in text


def test_runtime_schema_contract_contains_all_phase8_tables_and_columns() -> None:
    required = init_db._required_schema()
    assert PHASE8_TABLES <= set(required)
    assert {
        "user_id",
        "target_job_id",
        "application_id",
        "analysis_job_id",
        "consent_audio",
        "consent_camera",
        "consent_recording",
    } <= required["interview_realtime_sessions"]
    assert {"event_sequence", "redacted_payload_json", "payload_hash"} <= required[
        "interview_realtime_events"
    ]
    assert "interview_media_artifacts" not in required


@pytest.mark.skipif(
    not os.environ.get("DATABASE_URL", "").startswith("postgresql"),
    reason="requires the disposable PostgreSQL migration job",
)
def test_disposable_postgres_phase8_schema_and_runtime_validator() -> None:
    database_url = os.environ["DATABASE_URL"]
    engine = create_engine(database_url, future=True)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names(schema="public"))
    assert PHASE8_TABLES <= tables
    assert "interview_media_artifacts" not in tables

    session_fks = {
        (tuple(fk["constrained_columns"]), fk["referred_table"])
        for fk in inspector.get_foreign_keys("interview_realtime_sessions")
    }
    assert (("user_id",), "users") in session_fks
    assert (("target_job_id",), "applications") in session_fks
    assert (("application_id",), "applications") in session_fks
    assert (("analysis_job_id",), "analysis_jobs") in session_fks

    turn_uniques = {
        tuple(constraint["column_names"])
        for constraint in inspector.get_unique_constraints("interview_realtime_turns")
    }
    event_uniques = {
        tuple(constraint["column_names"])
        for constraint in inspector.get_unique_constraints("interview_realtime_events")
    }
    assert ("session_id", "turn_index") in turn_uniques
    assert ("session_id", "event_sequence") in event_uniques

    summary_indexes = {
        tuple(index["column_names"]): bool(index.get("unique"))
        for index in inspector.get_indexes("interview_realtime_summaries")
    }
    assert summary_indexes[("session_id",)] is True

    original_engine = init_db.engine
    try:
        init_db.engine = engine
        init_db.check_runtime_schema()
    finally:
        init_db.engine = original_engine
