from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

from sqlalchemy.exc import SQLAlchemyError

from check_db_schema import SchemaCheckResult, check_schema, print_schema_result


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"


def _run_alembic(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    return subprocess.run(
        ["alembic", *args],
        cwd=BACKEND_DIR,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def get_head_revision() -> str:
    result = _run_alembic(["heads"])
    if result.returncode != 0:
        print("failed to read Alembic heads", file=sys.stderr)
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(2)

    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped.split()[0]

    print("failed to parse Alembic head revision", file=sys.stderr)
    raise SystemExit(2)


def classify_adoption(result: SchemaCheckResult, head_revision: str) -> str:
    if result.appears_empty:
        return "empty"

    if result.missing_items:
        return "mismatch"

    if not result.alembic_version_exists or not result.alembic_versions:
        return "stamp"

    if result.alembic_versions == [head_revision]:
        return "already_head"

    return "version_mismatch"


def _print_safe_context(result: SchemaCheckResult, action: str) -> None:
    print(f"database dialect: {result.dialect or 'unknown'}")
    print(f"application tables present: {len(result.app_tables_present)}")
    print(f"alembic adoption action: {action}")


def stamp_head() -> int:
    result = _run_alembic(["stamp", "head"])
    if result.returncode != 0:
        print("alembic stamp head failed", file=sys.stderr)
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        return result.returncode

    print("alembic stamp head completed")
    return 0


def upgrade_head() -> int:
    result = _run_alembic(["upgrade", "head"])
    if result.returncode != 0:
        print("alembic upgrade head failed", file=sys.stderr)
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        return result.returncode

    print("alembic upgrade head completed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safely adopt an existing create_all-created database into Alembic tracking."
    )
    parser.add_argument(
        "--allow-empty-upgrade",
        action="store_true",
        help="Run alembic upgrade head only if the database appears empty.",
    )
    args = parser.parse_args()

    if not os.environ.get("DATABASE_URL"):
        print("DATABASE_URL is required; value was not printed.", file=sys.stderr)
        return 2

    try:
        schema_result = check_schema(os.environ["DATABASE_URL"])
    except SQLAlchemyError as exc:
        print(f"schema check failed: {exc.__class__.__name__}", file=sys.stderr)
        return 2

    print_schema_result(schema_result)
    head_revision = get_head_revision()
    action = classify_adoption(schema_result, head_revision)
    _print_safe_context(schema_result, action)

    if action == "mismatch":
        print("schema mismatch detected; refusing to stamp")
        return 1

    if action == "version_mismatch":
        print("alembic_version is present but not at head; refusing to stamp")
        return 1

    if action == "already_head":
        print("database is already adopted at Alembic head")
        return 0

    if action == "empty":
        if not args.allow_empty_upgrade:
            print(
                "database appears empty; alembic upgrade head may be appropriate, "
                "but was not run without --allow-empty-upgrade"
            )
            return 1

        return upgrade_head()

    if action == "stamp":
        return stamp_head()

    print(f"unknown adoption action: {action}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
