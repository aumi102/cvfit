from pathlib import Path
import os
import tempfile


_PYTEST_TMP = Path(__file__).resolve().parent / "backend" / "pytest-tmp"
_PYTEST_TMP.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("TMP", str(_PYTEST_TMP))
os.environ.setdefault("TEMP", str(_PYTEST_TMP))
tempfile.tempdir = str(_PYTEST_TMP)
