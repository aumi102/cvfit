import os
import importlib.util
from pathlib import Path
import sys


os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _load_adoption_module():
    scripts_dir = BACKEND_ROOT.parent / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    module_path = scripts_dir / "adopt_existing_db_with_alembic.py"
    spec = importlib.util.spec_from_file_location("adopt_existing_db_with_alembic", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_alembic_config_exists():
    assert (BACKEND_ROOT / "alembic.ini").is_file()
    assert (BACKEND_ROOT / "alembic" / "env.py").is_file()


def test_initial_migration_exists_and_mentions_current_schema():
    migration = BACKEND_ROOT / "alembic" / "versions" / "20260522_0001_initial_schema.py"

    text = migration.read_text(encoding="utf-8")

    assert "CREATE EXTENSION IF NOT EXISTS vector" in text
    assert '"cv_files"' in text
    assert '"jd_docs"' in text
    assert '"analysis_jobs"' in text
    assert '"text_embeddings"' in text
    assert '"access_token_hash"' in text


def test_models_still_import():
    from app.db import models

    assert models.CVFile.__tablename__ == "cv_files"
    assert models.JDDoc.__tablename__ == "jd_docs"
    assert models.AnalysisJob.__tablename__ == "analysis_jobs"
    assert models.TextEmbedding.__tablename__ == "text_embeddings"


def test_schema_checker_script_tracks_baseline_schema():
    script = BACKEND_ROOT.parent / "scripts" / "check_db_schema.py"

    text = script.read_text(encoding="utf-8")

    assert "REQUIRED_SCHEMA" in text
    assert '"analysis_jobs"' in text
    assert '"access_token_hash"' in text
    assert "alembic_version" in text


def test_adoption_logic_refuses_schema_mismatch():
    module = _load_adoption_module()
    result = module.SchemaCheckResult(
        required_tables={"analysis_jobs": {"id", "access_token_hash"}},
        existing_tables={"analysis_jobs"},
        missing_items=["analysis_jobs.access_token_hash"],
        alembic_versions=[],
        vector_extension_exists=True,
        dialect="postgresql",
    )

    assert module.classify_adoption(result, "20260522_0001") == "mismatch"


def test_adoption_logic_allows_stamp_for_matching_unstamped_schema():
    module = _load_adoption_module()
    result = module.SchemaCheckResult(
        required_tables={"analysis_jobs": {"id"}},
        existing_tables={"analysis_jobs"},
        missing_items=[],
        alembic_versions=[],
        vector_extension_exists=True,
        dialect="postgresql",
    )

    assert module.classify_adoption(result, "20260522_0001") == "stamp"


def test_adoption_logic_treats_head_as_already_adopted():
    module = _load_adoption_module()
    result = module.SchemaCheckResult(
        required_tables={"analysis_jobs": {"id"}},
        existing_tables={"analysis_jobs", "alembic_version"},
        missing_items=[],
        alembic_versions=["20260522_0001"],
        vector_extension_exists=True,
        dialect="postgresql",
    )

    assert module.classify_adoption(result, "20260522_0001") == "already_head"


def test_adoption_script_requires_database_url_without_printing_secret(monkeypatch, capsys):
    module = _load_adoption_module()

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(sys, "argv", ["adopt_existing_db_with_alembic.py"])

    assert module.main() == 2
    captured = capsys.readouterr()
    assert "DATABASE_URL is required" in captured.err
    assert "://" not in captured.err
