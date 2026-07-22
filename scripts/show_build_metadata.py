"""Print safe backend/worker build identity for deployment verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.build_metadata import safe_build_metadata  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", choices=("backend", "worker"), required=True)
    args = parser.parse_args()
    print(json.dumps(safe_build_metadata(args.service), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
