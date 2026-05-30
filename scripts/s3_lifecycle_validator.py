"""
S3 Lifecycle Validator & Cleanup Tool — Phase 1 Backend Quality

Mục đích:
  1. Kiểm tra lifecycle policy hiện tại của bucket có đúng như kỳ vọng.
  2. Validate rằng infra/s3-lifecycle.json hợp lệ.
  3. Gợi ý cách apply policy cho các S3-compatible providers.
  4. Cung cấp cleanup commands theo prefix.

Usage:
  # Check local infra/s3-lifecycle.json
  python scripts/s3_lifecycle_validator.py --validate-json

  # Validate remote bucket (requires AWS env vars or --profile)
  python scripts/s3_lifecycle_validator.py --check-bucket --bucket cvfit-prod

  # Show cleanup commands for a prefix
  python scripts/s3_lifecycle_validator.py --cleanup --bucket cvfit-prod --prefix uploads/

  # Dry-run list old objects (older than 30 days)
  python scripts/s3_lifecycle_validator.py --list-old --bucket cvfit-prod --days 30 --prefix uploads/

Chạy mà không cần AWS credentials để validate JSON schema.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
except ImportError:
    boto3 = None  # type: ignore

SCRIPT_DIR = Path(__file__).resolve().parent
INFRA_DIR = SCRIPT_DIR.parent / "infra"
DEFAULT_LIFECYCLE_JSON = INFRA_DIR / "s3-lifecycle.json"


@dataclass
class LifecycleRule:
    id: str
    prefix: str
    action_days: Optional[int] = None
    abort_days: Optional[int] = None
    status: str = "Enabled"

    def describe(self) -> str:
        if self.abort_days is not None:
            return f"  Rule '{self.id}': abort multipart after {self.abort_days}d | prefix='{self.prefix}' | {self.status}"
        return f"  Rule '{self.id}': expire after {self.action_days}d | prefix='{self.prefix}' | {self.status}"


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    rules: list[LifecycleRule] = field(default_factory=list)


def parse_lifecycle_json(path: Path) -> ValidationResult:
    """Parse and validate infra/s3-lifecycle.json schema and business rules."""
    result = ValidationResult(ok=True)

    if not path.exists():
        result.ok = False
        result.errors.append(f"Lifecycle JSON not found: {path}")
        return result

    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        result.ok = False
        result.errors.append(f"Invalid JSON: {exc}")
        return result

    if not isinstance(data, dict) or "Rules" not in data:
        result.ok = False
        result.errors.append("Root must be a dict with a 'Rules' key")
        return result

    rules: list[dict] = data["Rules"]
    if not rules:
        result.errors.append("No rules defined — bucket objects will never expire")
        result.warnings.append("Add lifecycle rules for uploads/, reports/, tmp/")
        result.ok = False
        return result

    seen_ids: set[str] = set()
    expected_prefixes = {"tmp/", "uploads/", "reports/"}

    for i, rule in enumerate(rules):
        rule_id = rule.get("ID", f"<rule #{i}>")
        if rule_id in seen_ids:
            result.warnings.append(f"Duplicate rule ID '{rule_id}'")
        seen_ids.add(rule_id)

        status = rule.get("Status", "Disabled")
        filter_dict = rule.get("Filter", {})
        prefix = filter_dict.get("Prefix", "") if isinstance(filter_dict, dict) else ""

        if not isinstance(rule, dict):
            result.ok = False
            result.errors.append(f"Rule at index {i} is not an object")
            continue

        if status != "Enabled":
            result.warnings.append(f"Rule '{rule_id}' has Status='{status}' (not Enabled)")

        expiration = rule.get("Expiration")
        abort_mpu = rule.get("AbortIncompleteMultipartUpload")

        if expiration:
            days = expiration.get("Days")
            if days is None:
                result.ok = False
                result.errors.append(f"Rule '{rule_id}': Expiration has no 'Days'")
            elif days <= 0:
                result.ok = False
                result.errors.append(f"Rule '{rule_id}': Expiration.Days must be > 0, got {days}")
            elif days < 1:
                result.warnings.append(f"Rule '{rule_id}': Expiration.Days={days} means objects expire within 24h")
            result.rules.append(LifecycleRule(id=rule_id, prefix=prefix, action_days=days, status=status))
        elif abort_mpu:
            days_after = abort_mpu.get("DaysAfterInitiation")
            if days_after is None:
                result.ok = False
                result.errors.append(f"Rule '{rule_id}': AbortIncompleteMultipartUpload has no 'DaysAfterInitiation'")
            elif days_after <= 0:
                result.ok = False
                result.errors.append(f"Rule '{rule_id}': DaysAfterInitiation must be > 0, got {days_after}")
            result.rules.append(LifecycleRule(id=rule_id, prefix=prefix, abort_days=days_after, status=status))
        else:
            result.ok = False
            result.errors.append(
                f"Rule '{rule_id}': must have Expiration or AbortIncompleteMultipartUpload"
            )

    defined_prefixes = {r.prefix for r in result.rules}
    for expected in expected_prefixes:
        if expected not in defined_prefixes:
            result.warnings.append(f"Missing lifecycle rule for prefix '{expected}'")

    if not result.errors:
        result.ok = True
    return result


def _get_boto_client(service: str, profile: Optional[str] = None):
    if boto3 is None:
        raise RuntimeError("boto3 is not installed. Run: pip install boto3")
    kwargs: dict = {"service_name": service}
    if profile:
        kwargs["profile_name"] = profile
    return boto3.Session(profile_name=profile).client(service) if profile else boto3.client(service)


def check_remote_lifecycle(bucket: str, prefix: str = "", profile: Optional[str] = None) -> ValidationResult:
    """Fetch and validate the live lifecycle policy from the bucket."""
    result = ValidationResult(ok=True)
    client = _get_boto_client("s3", profile)

    try:
        resp = client.get_bucket_lifecycle_configuration(Bucket=bucket)
    except ClientError as exc:
        err_code = exc.response.get("Error", {}).get("Code", "")
        if err_code == "NoSuchLifecycleConfiguration":
            result.ok = False
            result.errors.append(f"No lifecycle configuration on bucket '{bucket}'")
            return result
        result.ok = False
        result.errors.append(f"AWS error: {exc}")
        return result
    except (NoCredentialsError, ProfileNotFound) as exc:
        result.ok = False
        result.errors.append(str(exc))
        return result

    raw_rules: list[dict] = resp.get("Rules", [])
    if not raw_rules:
        result.warnings.append("Bucket has empty lifecycle configuration")
        return result

    for rule in raw_rules:
        rule_id = rule.get("ID", "")
        status = rule.get("Status", "Disabled")
        filter_dict = rule.get("Filter", {})
        pf = filter_dict.get("Prefix", "") if isinstance(filter_dict, dict) else ""

        expiration = rule.get("Expiration")
        abort_mpu = rule.get("AbortIncompleteMultipartUpload")

        if expiration:
            days = expiration.get("Days")
            result.rules.append(LifecycleRule(id=rule_id, prefix=pf, action_days=days, status=status))
        elif abort_mpu:
            days_after = abort_mpu.get("DaysAfterInitiation")
            result.rules.append(LifecycleRule(id=rule_id, prefix=pf, abort_days=days_after, status=status))

    return result


def list_old_objects(bucket: str, prefix: str, days: int, profile: Optional[str] = None) -> list[str]:
    """Return list of S3 object keys older than `days` under prefix (dry-run)."""
    import datetime

    client = _get_boto_client("s3", profile)
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    old_keys: list[str] = []

    try:
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                last_modified = obj.get("LastModified")
                if last_modified and last_modified < cutoff:
                    old_keys.append(obj["Key"])
    except (NoCredentialsError, ProfileNotFound) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
    except ClientError as exc:
        print(f"[ERROR] AWS: {exc}", file=sys.stderr)

    return old_keys


def generate_cleanup_commands(
    bucket: str, prefix: str, dry_run: bool = True, execute: bool = False
) -> None:
    """Print safe cleanup commands for the given prefix.

    Args:
        dry_run: if True (default), only print the AWS CLI command.
        execute: if True, actually apply the lifecycle rule to the bucket.
                 Requires interactive confirmation.
    """
    mode_label = "DRY-RUN" if dry_run else "LIVE EXECUTION"
    print(f"\n# === {mode_label} ===")
    print(f"# Bucket : {bucket}")
    print(f"# Prefix : {prefix!r}\n")

    expire_days = 1 if prefix.startswith("tmp/") else 30
    rule_id = f"manual-cleanup-{prefix.rstrip('/').replace('/', '-') or 'all'}"

    cmd_common = (
        f"aws s3api put-bucket-lifecycle-configuration "
        f"--bucket {bucket} "
        f"--lifecycle-configuration '{{\n"
        f'  "Rules": [\n'
        f'    {{\n'
        f'      "ID": "{rule_id}",\n'
        f'      "Status": "Enabled",\n'
        f'      "Filter": {{ "Prefix": "{prefix}" }},\n'
        f'      "Expiration": {{ "Days": {expire_days} }}\n'
        f'    }}\n'
        f'  ]\n'
        f"}}'"
    )
    print(cmd_common)
    print()

    if execute:
        confirm = (
            input(f"Apply the above lifecycle rule to bucket '{bucket}'? [yes/no]: ")
            .strip()
            .lower()
        )
        if confirm != "yes":
            print("Cancelled — no changes made.")
            return
        try:
            import boto3
            client = boto3.client("s3")
            config = {
                "Rules": [
                    {
                        "ID": rule_id,
                        "Status": "Enabled",
                        "Filter": {"Prefix": prefix},
                        "Expiration": {"Days": expire_days},
                    }
                ]
            }
            client.put_bucket_lifecycle_configuration(
                Bucket=bucket, LifecycleConfiguration=config
            )
            print(f"[OK] Lifecycle rule applied to '{bucket}'.")
        except Exception as exc:
            print(f"[ERROR] Failed to apply rule: {exc}", file=sys.stderr)


def report_json_validation(path: Path) -> int:
    """Validate local JSON file. Returns 0 if OK, 1 if issues found."""
    print(f"\n=== Validating {path} ===\n")
    result = parse_lifecycle_json(path)

    for rule in result.rules:
        print(rule.describe())

    if result.warnings:
        print("\n[WARNINGS]")
        for w in result.warnings:
            print(f"  - {w}")

    if result.errors:
        print("\n[ERRORS]")
        for e in result.errors:
            print(f"  - {e}")

    if result.ok and not result.warnings:
        print("\n[PASS] Lifecycle JSON is valid and complete.")
    elif result.ok:
        print("\n[PASS with warnings] Lifecycle JSON is valid.")
    else:
        print("\n[FAIL] Lifecycle JSON has errors.")

    return 0 if result.ok else 1


def report_remote_validation(bucket: str, profile: Optional[str] = None) -> int:
    """Check remote bucket lifecycle. Returns 0 if OK, 1 otherwise."""
    print(f"\n=== Checking remote bucket: {bucket} ===\n")
    result = check_remote_lifecycle(bucket, profile=profile)

    if result.errors:
        for e in result.errors:
            print(f"[ERROR] {e}")
        return 1

    if not result.rules:
        print("[WARN] No lifecycle rules found on bucket.")
        return 1

    for rule in result.rules:
        print(rule.describe())

    if result.warnings:
        print("\n[WARNINGS]")
        for w in result.warnings:
            print(f"  - {w}")

    print("\n[PASS] Remote lifecycle policy retrieved.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="S3 Lifecycle Validator & Cleanup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--validate-json",
        metavar="PATH",
        const=DEFAULT_LIFECYCLE_JSON,
        nargs="?",
        type=Path,
        help="Validate local infra/s3-lifecycle.json. "
        "Defaults to infra/s3-lifecycle.json if no path given.",
    )
    parser.add_argument(
        "--check-bucket",
        metavar="BUCKET",
        help="Fetch and validate the live lifecycle policy from an S3 bucket.",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Print safe cleanup lifecycle commands for a prefix.",
    )
    parser.add_argument(
        "--list-old",
        action="store_true",
        help="List objects older than --days under --prefix (dry-run).",
    )
    parser.add_argument("--bucket", metavar="NAME", help="S3 bucket name for remote operations.")
    parser.add_argument(
        "--prefix",
        metavar="PREFIX",
        default="",
        help="S3 prefix for cleanup/list operations (e.g. uploads/, reports/, tmp/).",
    )
    parser.add_argument(
        "--days",
        metavar="N",
        type=int,
        default=30,
        help="Days threshold for --list-old (default: 30).",
    )
    parser.add_argument(
        "--profile",
        metavar="NAME",
        help="AWS CLI profile to use instead of environment credentials.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually apply the lifecycle rule to the bucket (interactive confirmation required). "
        "Without this flag, cleanup only prints the AWS CLI command (dry-run).",
    )

    args = parser.parse_args(argv)

    if args.validate_json:
        return report_json_validation(args.validate_json)

    if args.check_bucket:
        if not args.bucket:
            print("[ERROR] --bucket required for --check-bucket", file=sys.stderr)
            return 1
        return report_remote_validation(args.check_bucket, profile=args.profile)

    if args.cleanup:
        if not args.bucket:
            print("[ERROR] --bucket required for --cleanup", file=sys.stderr)
            return 1
        if not args.prefix:
            print("[ERROR] --prefix required for --cleanup", file=sys.stderr)
            return 1
        generate_cleanup_commands(args.bucket, args.prefix, execute=args.execute)
        return 0

    if args.list_old:
        if not args.bucket:
            print("[ERROR] --bucket required for --list-old", file=sys.stderr)
            return 1
        if boto3 is None:
            print("[ERROR] boto3 not installed. Run: pip install boto3", file=sys.stderr)
            return 1
        print(f"\n=== Listing objects older than {args.days} days under '{args.prefix}' in {args.bucket} ===\n")
        keys = list_old_objects(args.bucket, args.prefix, args.days)
        if not keys:
            print("  No old objects found.")
        else:
            print(f"  Found {len(keys)} old object(s):")
            for k in keys[:20]:
                print(f"    {k}")
            if len(keys) > 20:
                print(f"    ... and {len(keys) - 20} more")
        return 0

    parser.print_help()
    print("\n[INFO] Tip: Validate the local JSON first, then check the remote bucket:")
    print(f"  python {Path(__file__).name} --validate-json")
    print(f"  python {Path(__file__).name} --check-bucket cvfit-prod")
    print(f"  python {Path(__file__).name} --list-old --bucket cvfit-prod --prefix uploads/ --days 30")
    print(f"  python {Path(__file__).name} --cleanup --bucket cvfit-prod --prefix uploads/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
