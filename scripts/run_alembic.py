from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
ALEMBIC_SCRIPT_LOCATION = BACKEND_DIR / "alembic"


def parse_command(argv: list[str]) -> tuple[str, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run project Alembic commands through Python without relying on an alembic executable."
    )
    parser.add_argument("command", choices=("current", "heads", "history", "upgrade"))
    parser.add_argument("args", nargs=argparse.REMAINDER)
    namespace = parser.parse_args(argv)

    if namespace.command == "upgrade":
        if len(namespace.args) != 1:
            parser.error("upgrade requires exactly one revision, for example: upgrade head")
    elif namespace.args:
        parser.error(f"{namespace.command} does not accept extra arguments")

    return namespace.command, namespace.args


def _remove_backend_paths_before_import() -> None:
    backend_root = BACKEND_DIR.resolve()
    alembic_dir = ALEMBIC_SCRIPT_LOCATION.resolve()
    filtered_paths: list[str] = []

    for entry in sys.path:
        candidate = Path(entry or os.getcwd()).resolve()
        if candidate in {backend_root, alembic_dir}:
            continue
        filtered_paths.append(entry)

    sys.path[:] = filtered_paths


def _load_alembic_api():
    _remove_backend_paths_before_import()
    try:
        from alembic import command
        from alembic.config import Config
    except ModuleNotFoundError as exc:
        if exc.name == "alembic":
            print(
                "Alembic is not installed. Install backend/requirements.txt in this environment.",
                file=sys.stderr,
            )
            raise SystemExit(2) from exc
        raise

    return command, Config


def build_config(config_cls):
    config = config_cls(str(ALEMBIC_INI))
    config.set_main_option("script_location", str(ALEMBIC_SCRIPT_LOCATION))
    config.set_main_option("prepend_sys_path", str(BACKEND_DIR))
    config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"].replace("%", "%%"))
    return config


def run_command(command_name: str, command_args: list[str]) -> None:
    alembic_command, config_cls = _load_alembic_api()
    config = build_config(config_cls)

    if command_name == "current":
        alembic_command.current(config)
    elif command_name == "heads":
        alembic_command.heads(config)
    elif command_name == "history":
        alembic_command.history(config)
    elif command_name == "upgrade":
        alembic_command.upgrade(config, command_args[0])
    else:
        raise AssertionError(f"unsupported Alembic command: {command_name}")


def main(argv: list[str] | None = None) -> int:
    if not os.environ.get("DATABASE_URL"):
        print("DATABASE_URL is required; value was not printed.", file=sys.stderr)
        return 2

    if not ALEMBIC_INI.is_file():
        print(f"Alembic config not found: {ALEMBIC_INI}", file=sys.stderr)
        return 2

    command_name, command_args = parse_command(sys.argv[1:] if argv is None else argv)

    # backend/alembic/env.py imports app settings, which require REDIS_URL even
    # though migrations do not use Redis.
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

    run_command(command_name, command_args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
