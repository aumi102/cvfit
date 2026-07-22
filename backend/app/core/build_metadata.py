"""Allowlisted, non-sensitive deployment metadata shared by backend and worker."""

from __future__ import annotations

from datetime import datetime
import os
import re
from typing import Mapping


_COMMIT_SHA = re.compile(r"^[0-9a-fA-F]{7,40}$")
_ENVIRONMENTS = {"development", "test", "staging", "production"}


def safe_build_metadata(
    service: str,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str | None]:
    """Return only allowlisted public build fields; never dump the environment."""
    values = environ if environ is not None else os.environ
    raw_sha = values.get("RENDER_GIT_COMMIT") or values.get("BUILD_COMMIT_SHA") or ""
    commit_sha = raw_sha.lower() if _COMMIT_SHA.fullmatch(raw_sha) else "unknown"

    raw_environment = values.get("APP_ENVIRONMENT", "").strip().lower()
    if not raw_environment and values.get("RENDER", "").lower() == "true":
        raw_environment = "production"
    environment = raw_environment if raw_environment in _ENVIRONMENTS else "unknown"

    raw_build_time = values.get("BUILD_TIME", "").strip()
    build_time = _safe_iso_datetime(raw_build_time)
    return {
        "service": service,
        "commit_sha": commit_sha,
        "environment": environment,
        "build_time": build_time,
    }


def _safe_iso_datetime(value: str) -> str | None:
    if not value or len(value) > 40:
        return None
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return value
