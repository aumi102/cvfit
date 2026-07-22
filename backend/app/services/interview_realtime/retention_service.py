"""Data-minimizing retention operations for Phase 8 realtime interviews."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import InterviewRealtimeSession


REALTIME_INTERVIEW_RETENTION_DAYS = 30
MAX_RETENTION_PURGE_BATCH = 500


@dataclass(frozen=True)
class RetentionPurgeResult:
    cutoff: datetime
    candidates: int
    deleted: int
    dry_run: bool


def purge_expired_realtime_sessions(
    db: Session,
    *,
    now: datetime | None = None,
    retention_days: int = REALTIME_INTERVIEW_RETENTION_DAYS,
    batch_limit: int = MAX_RETENTION_PURGE_BATCH,
    dry_run: bool = True,
) -> RetentionPurgeResult:
    """Delete a bounded batch older than the policy cutoff; dry-run by default."""
    if retention_days < 1:
        raise ValueError("retention_days must be at least 1")
    if not 1 <= batch_limit <= MAX_RETENTION_PURGE_BATCH:
        raise ValueError(
            f"batch_limit must be between 1 and {MAX_RETENTION_PURGE_BATCH}"
        )

    cutoff = (now or datetime.utcnow()) - timedelta(days=retention_days)
    candidates = (
        db.query(InterviewRealtimeSession)
        .filter(InterviewRealtimeSession.updated_at < cutoff)
        .order_by(InterviewRealtimeSession.updated_at.asc())
        .limit(batch_limit)
        .all()
    )
    if not dry_run:
        for session in candidates:
            db.delete(session)
        db.commit()

    return RetentionPurgeResult(
        cutoff=cutoff,
        candidates=len(candidates),
        deleted=0 if dry_run else len(candidates),
        dry_run=dry_run,
    )
