"""Operator-safe Phase 8 retention purge. Defaults to a non-mutating dry-run."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.session import SessionLocal  # noqa: E402
from app.services.interview_realtime.retention_service import (  # noqa: E402
    MAX_RETENTION_PURGE_BATCH,
    REALTIME_INTERVIEW_RETENTION_DAYS,
    purge_expired_realtime_sessions,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Purge expired realtime interview sessions in a bounded batch."
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=REALTIME_INTERVIEW_RETENTION_DAYS,
    )
    parser.add_argument(
        "--batch-limit",
        type=int,
        default=MAX_RETENTION_PURGE_BATCH,
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Perform deletion. Without this flag the command is a dry-run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with SessionLocal() as db:
        result = purge_expired_realtime_sessions(
            db,
            retention_days=args.retention_days,
            batch_limit=args.batch_limit,
            dry_run=not args.execute,
        )
    mode = "execute" if args.execute else "dry-run"
    print(
        f"realtime-retention mode={mode} candidates={result.candidates} "
        f"deleted={result.deleted} cutoff={result.cutoff.isoformat()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
