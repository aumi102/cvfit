"""Tests for scripts/s3_lifecycle_validator.py"""

import json
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
import sys

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import s3_lifecycle_validator as validator


def _write_lifecycle(path: Path, rules: list[dict]) -> None:
    path.write_text(json.dumps({"Rules": rules}, indent=2), encoding="utf-8")


class TestParseLifecycleJson:
    def test_valid_lifecycle_passes(self, tmp_path):
        path = tmp_path / "lifecycle.json"
        _write_lifecycle(path, [
            {"ID": "expire-tmp", "Status": "Enabled", "Filter": {"Prefix": "tmp/"}, "Expiration": {"Days": 1}},
            {"ID": "expire-uploads", "Status": "Enabled", "Filter": {"Prefix": "uploads/"}, "Expiration": {"Days": 30}},
            {"ID": "expire-reports", "Status": "Enabled", "Filter": {"Prefix": "reports/"}, "Expiration": {"Days": 30}},
            {
                "ID": "abort-mpu",
                "Status": "Enabled",
                "Filter": {"Prefix": ""},
                "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7},
            },
        ])
        result = validator.parse_lifecycle_json(path)
        assert result.ok is True
        assert len(result.rules) == 4
        assert {r.id for r in result.rules} == {
            "expire-tmp", "expire-uploads", "expire-reports", "abort-mpu"
        }

    def test_missing_file_returns_error(self, tmp_path):
        path = tmp_path / "nonexistent.json"
        result = validator.parse_lifecycle_json(path)
        assert result.ok is False
        assert any("not found" in e for e in result.errors)

    def test_invalid_json_returns_error(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{invalid json}", encoding="utf-8")
        result = validator.parse_lifecycle_json(path)
        assert result.ok is False
        assert any("JSON" in e for e in result.errors)

    def test_missing_rules_key_returns_error(self, tmp_path):
        path = tmp_path / "norules.json"
        path.write_text(json.dumps({"NotRules": []}), encoding="utf-8")
        result = validator.parse_lifecycle_json(path)
        assert result.ok is False
        assert any("Rules" in e for e in result.errors)

    def test_empty_rules_adds_error(self, tmp_path):
        path = tmp_path / "norules.json"
        _write_lifecycle(path, [])
        result = validator.parse_lifecycle_json(path)
        assert result.ok is False
        assert any("No rules" in e for e in result.errors)

    def test_disabled_rule_adds_warning(self, tmp_path):
        path = tmp_path / "disabled.json"
        _write_lifecycle(path, [
            {"ID": "disabled-rule", "Status": "Disabled", "Filter": {"Prefix": "tmp/"}, "Expiration": {"Days": 1}}
        ])
        result = validator.parse_lifecycle_json(path)
        assert result.ok is True
        assert any("Enabled" in w for w in result.warnings)

    def test_missing_expiration_and_abort_adds_error(self, tmp_path):
        path = tmp_path / "norule.json"
        _write_lifecycle(path, [
            {"ID": "noop-rule", "Status": "Enabled", "Filter": {"Prefix": "uploads/"}}
        ])
        result = validator.parse_lifecycle_json(path)
        assert result.ok is False
        assert any("must have Expiration or AbortIncompleteMultipartUpload" in e for e in result.errors)

    def test_expiration_days_must_be_positive(self, tmp_path):
        path = tmp_path / "zero-days.json"
        _write_lifecycle(path, [
            {"ID": "zero-days", "Status": "Enabled", "Filter": {"Prefix": "tmp/"}, "Expiration": {"Days": 0}}
        ])
        result = validator.parse_lifecycle_json(path)
        assert result.ok is False
        assert any("must be > 0" in e for e in result.errors)

    def test_warns_missing_required_prefixes(self, tmp_path):
        path = tmp_path / "partial.json"
        _write_lifecycle(path, [
            {"ID": "expire-tmp", "Status": "Enabled", "Filter": {"Prefix": "tmp/"}, "Expiration": {"Days": 1}}
        ])
        result = validator.parse_lifecycle_json(path)
        assert result.ok is True
        assert any("uploads/" in w for w in result.warnings)
        assert any("reports/" in w for w in result.warnings)

    def test_duplicate_rule_id_adds_warning(self, tmp_path):
        path = tmp_path / "dup.json"
        _write_lifecycle(path, [
            {"ID": "dup-rule", "Status": "Enabled", "Filter": {"Prefix": "tmp/"}, "Expiration": {"Days": 1}},
            {"ID": "dup-rule", "Status": "Enabled", "Filter": {"Prefix": "uploads/"}, "Expiration": {"Days": 30}},
        ])
        result = validator.parse_lifecycle_json(path)
        assert any("Duplicate" in w for w in result.warnings)


class TestGenerateCleanupCommands:
    def test_dry_run_prints_command(self, capsys):
        validator.generate_cleanup_commands("test-bucket", "uploads/")
        output = capsys.readouterr().out
        assert "DRY-RUN" in output
        assert "test-bucket" in output
        assert "uploads/" in output
        assert "put-bucket-lifecycle-configuration" in output

    def test_dry_run_flag_shows_correct_label(self, capsys):
        validator.generate_cleanup_commands("my-bucket", "tmp/", dry_run=True)
        output = capsys.readouterr().out
        assert "DRY-RUN" in output
        assert "my-bucket" in output

    def test_cleanup_without_execute_does_not_prompt(self, monkeypatch):
        """Without --execute, generate_cleanup_commands must not call boto3."""
        called = False
        def fake_boto3_client(*args, **kwargs):
            nonlocal called
            called = True
            raise RuntimeError("should not be called")
        import s3_lifecycle_validator as mod
        monkeypatch.setattr(mod, "boto3", type("FakeBoto3", (), {"client": fake_boto3_client}))
        validator.generate_cleanup_commands("bucket", "uploads/", dry_run=True, execute=False)
        assert not called


class TestMainCli:
    def test_validate_json_reports_ok(self, tmp_path):
        path = tmp_path / "good.json"
        _write_lifecycle(path, [
            {"ID": "expire-tmp", "Status": "Enabled", "Filter": {"Prefix": "tmp/"}, "Expiration": {"Days": 1}},
            {"ID": "abort-mpu", "Status": "Enabled", "Filter": {"Prefix": ""}, "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}},
        ])
        exit_code = validator.main(["--validate-json", str(path)])
        assert exit_code == 0

    def test_validate_json_reports_fail_for_missing_file(self, tmp_path):
        path = tmp_path / "missing.json"
        exit_code = validator.main(["--validate-json", str(path)])
        assert exit_code == 1

    def test_validate_default_json_exists(self):
        exit_code = validator.main(["--validate-json"])
        assert exit_code == 0

    def test_missing_bucket_flag_shows_error(self):
        exit_code = validator.main(["--check-bucket", "some-bucket"])
        assert exit_code == 1

    def test_missing_prefix_flag_shows_error(self):
        exit_code = validator.main(["--cleanup", "--bucket", "my-bucket"])
        assert exit_code == 1

    def test_missing_bucket_for_list_old_shows_error(self):
        exit_code = validator.main(["--list-old"])
        assert exit_code == 1

    def test_help_shows_no_error(self):
        with pytest.raises(SystemExit) as exc:
            validator.main(["--help"])
        assert exc.value.code == 0

    def test_help_includes_execute_flag(self):
        import io, sys
        old_stdout = sys.stdout
        try:
            sys.stdout = io.StringIO()
            try:
                validator.main(["--help"])
            except SystemExit:
                pass
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        assert "--execute" in output
