from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import sys
import warnings

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import SAWarning


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# The runtime validator is authoritative. Importing it here prevents this
# operator checker from drifting behind newer application tables or columns.
_database_url_was_missing = "DATABASE_URL" not in os.environ
_redis_url_was_missing = "REDIS_URL" not in os.environ
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
from app.db.init_db import EXPECTED_ALEMBIC_HEAD, _required_schema  # noqa: E402
if _database_url_was_missing:
    os.environ.pop("DATABASE_URL", None)
if _redis_url_was_missing:
    os.environ.pop("REDIS_URL", None)


REQUIRED_SCHEMA = _required_schema()


@dataclass(frozen=True)
class SchemaCheckResult:
    required_tables: dict[str, set[str]]
    existing_tables: set[str]
    missing_items: list[str]
    alembic_versions: list[str]
    vector_extension_exists: bool | None
    dialect: str | None
    expected_alembic_head: str | None = None

    @property
    def baseline_matches(self) -> bool:
        return not self.missing_items

    @property
    def alembic_version_exists(self) -> bool:
        return "alembic_version" in self.existing_tables

    @property
    def app_tables_present(self) -> set[str]:
        return set(self.required_tables) & self.existing_tables

    @property
    def app_tables_missing(self) -> set[str]:
        return set(self.required_tables) - self.existing_tables

    @property
    def appears_empty(self) -> bool:
        return not self.app_tables_present and not self.alembic_version_exists

    @property
    def alembic_head_matches(self) -> bool:
        return (
            self.expected_alembic_head is not None
            and self.alembic_versions == [self.expected_alembic_head]
        )


def _print_status(label: str, ok: bool, detail: str = "") -> None:
    status = "ok" if ok else "missing"
    suffix = f": {detail}" if detail else ""
    print(f"{label}: {status}{suffix}")


def check_schema(database_url: str) -> SchemaCheckResult:
    warnings.filterwarnings(
        "ignore",
        message="Did not recognize type 'vector'.*",
        category=SAWarning,
    )

    engine = create_engine(database_url, future=True)
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names(schema="public"))

    missing_items: list[str] = []
    for table, required_columns in REQUIRED_SCHEMA.items():
        if table not in existing_tables:
            missing_items.append(table)
            continue

        existing_columns = {column["name"] for column in inspector.get_columns(table)}
        missing_columns = sorted(required_columns - existing_columns)
        missing_items.extend(f"{table}.{column}" for column in missing_columns)

    alembic_versions: list[str] = []
    vector_extension_exists: bool | None = None
    dialect: str | None = None

    with engine.connect() as connection:
        dialect = connection.dialect.name
        if "alembic_version" in existing_tables:
            alembic_versions = [
                str(row[0])
                for row in connection.execute(text("SELECT version_num FROM alembic_version"))
            ]
            if alembic_versions != [EXPECTED_ALEMBIC_HEAD]:
                current = ", ".join(sorted(alembic_versions)) or "<none>"
                missing_items.append(
                    f"alembic head (expected {EXPECTED_ALEMBIC_HEAD}, found {current})"
                )

        if dialect == "postgresql":
            vector_extension_exists = (
                connection.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).scalar()
                is not None
            )
            if not vector_extension_exists:
                missing_items.append("vector extension")

    return SchemaCheckResult(
        required_tables=REQUIRED_SCHEMA,
        existing_tables=existing_tables,
        missing_items=missing_items,
        alembic_versions=alembic_versions,
        vector_extension_exists=vector_extension_exists,
        dialect=dialect,
        expected_alembic_head=EXPECTED_ALEMBIC_HEAD,
    )


def print_schema_result(result: SchemaCheckResult) -> None:
    for table, required_columns in result.required_tables.items():
        if table not in result.existing_tables:
            _print_status(table, False)
            continue

        missing_columns = sorted(
            item.split(".", 1)[1]
            for item in result.missing_items
            if item.startswith(f"{table}.")
        )
        if missing_columns:
            _print_status(table, False, ", ".join(missing_columns))
        else:
            _print_status(table, True)

    _print_status("alembic_version table", result.alembic_version_exists)
    if result.alembic_version_exists:
        current = ", ".join(sorted(result.alembic_versions)) or "<none>"
        _print_status(
            "alembic expected head",
            result.alembic_head_matches,
            f"expected {result.expected_alembic_head}, found {current}",
        )

    if result.vector_extension_exists is None:
        print(f"vector extension: skipped for {result.dialect}")
    else:
        _print_status("vector extension", result.vector_extension_exists)


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is required; value was not printed.", file=sys.stderr)
        return 2

    try:
        result = check_schema(database_url)

    except SQLAlchemyError as exc:
        print(f"schema check failed: {exc.__class__.__name__}", file=sys.stderr)
        return 2

    print_schema_result(result)
    if result.missing_items:
        print("baseline schema check failed")
        return 1

    print("current runtime schema check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
