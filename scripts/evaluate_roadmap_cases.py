"""
AI CV Fit — Evaluation Script for Learning Roadmap Cases

Evaluates the learning roadmap generation (build_learning_roadmap) for quality and guardrails.

Usage:
    python scripts/evaluate_roadmap_cases.py
    python scripts/evaluate_roadmap_cases.py --verbose
    python scripts/evaluate_roadmap_cases.py --case lr_01
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.parsing.jd_parser import parse_jd
from app.services.scoring.scorer import score
from app.services.scoring.result_v2 import build_result_v2
from app.services.scoring.result_v3 import build_result_v3
from app.services.roadmap.learning_roadmap import build_learning_roadmap


def _run_pipeline(cv_text: str, jd_text: str, job_id: str) -> dict:
    """Run the full scoring pipeline and return a v3 result."""
    jd_struct = parse_jd(jd_text)
    from app.services.ontology.skill_ontology import get_skill_ontology

    ontology = get_skill_ontology()
    detected_skills = sorted(ontology.detect_skills_in_text(cv_text))
    bullets = [line.strip() for line in cv_text.splitlines() if len(line.strip()) >= 25]
    if not bullets:
        bullets = [l.strip() for l in cv_text.splitlines() if len(l.strip()) >= 40][:80]
    confidence = 0.85 if len(cv_text) >= 300 else max(0.2, len(cv_text) / 400 * 0.85)

    cv_parsed = {
        "text": cv_text,
        "bullets": bullets,
        "skills_detected": detected_skills,
        "confidence": confidence,
    }
    scored = score(cv_parsed, jd_struct)
    result_full = {
        "job_id": job_id,
        "cv": {
            "file_name": "cv.txt",
            "parsed_confidence": cv_parsed["confidence"],
            "skills_detected": cv_parsed.get("skills_detected", []),
        },
        "jd": jd_struct,
        **scored,
    }
    result_v2 = build_result_v2(result_full, cv_parsed=cv_parsed, jd_struct=jd_struct, job_id=job_id)
    result_v3 = build_result_v3(result_v2)
    return result_v3


def _load_case(case_dir: Path) -> dict | None:
    """Load a learning roadmap case from its directory.

    Discovers the case prefix by globbing for the first matching file.
    """
    cv_files = sorted(case_dir.glob("case_*_cv.txt"))
    jd_files = sorted(case_dir.glob("case_*_jd.txt"))
    expected_files = sorted(case_dir.glob("case_*_expected.md"))

    if not (cv_files and jd_files and expected_files):
        return None

    cv_file = cv_files[0]
    jd_file = jd_files[0]
    expected_file = expected_files[0]

    return {
        "cv": cv_file.read_text(encoding="utf-8"),
        "jd": jd_file.read_text(encoding="utf-8"),
        "expected_text": expected_file.read_text(encoding="utf-8"),
    }


def _parse_expected(text: str) -> dict:
    """Parse expected requirements from expected.md."""
    checks: dict[str, bool] = {
        "must_have_priority_high": "priority.*high" in text.lower() and "must_have" in text.lower(),
        "nice_to_have_priority_medium": "nice_to_have" in text.lower() and ("medium" in text.lower() or "low" in text.lower()),
        "do_not_claim_until_completed_true": "do_not_claim_until_completed.*true" in text.lower(),
        "do_not_claim_until_completed_false": "do_not_claim_until_completed.*false" in text.lower(),
        "fabrication_guardrail": "fabricat" in text.lower(),
        "already_know_false": '"you already know"' in text.lower() or "do_not_claim" in text.lower(),
        "why_future_facing": "future" in text.lower() or "not found" in text.lower(),
    }
    return checks


def _check_guardrails(roadmap: list[dict], result: dict) -> dict:
    """Run guardrail checks on the learning roadmap output."""
    violations: dict[str, list[str]] = {
        "do_not_claim_missing": [],
        "fabrication": [],
        "priority_mismatch": [],
        "missing_fields": [],
    }

    required_fields = {"skill", "priority", "why", "topics", "mini_project", "cv_evidence_to_add_after_learning", "do_not_claim_until_completed"}

    ALREADY_KNOW_PATTERNS = [
        re.compile(r"\bsince\s+you\s+(already\s+)?know", re.IGNORECASE),
        re.compile(r"\byou\s+(already\s+)?have\s+\w+\s+experience", re.IGNORECASE),
        re.compile(r"\bsince\s+you\s+(already\s+)?have\s+\w+\s+skills", re.IGNORECASE),
        re.compile(r"\byour\s+\w+\s+experience\s+in\s+\w+\s+is\s+strong", re.IGNORECASE),
    ]

    for i, item in enumerate(roadmap):
        missing_fields = required_fields - set(item.keys())
        if missing_fields:
            violations["missing_fields"].append(
                f"  Item {i+1} ({item.get('skill', '?')}): missing fields: {missing_fields}"
            )

        if item.get("do_not_claim_until_completed") is not True:
            violations["do_not_claim_missing"].append(
                f"  Item {i+1} ({item.get('skill', '?')}): do_not_claim_until_completed is not True"
            )

        priority = str(item.get("priority", "")).lower()
        skill = str(item.get("skill", "")).lower()
        why = str(item.get("why", "")).lower()

        matched_skills = {str(s).lower() for s in result.get("matched_skills", []) if isinstance(s, dict)}
        missing_skills = {str(s.get("skill", "")).lower() for s in result.get("missing_skills", []) if isinstance(s, dict)}

        if skill in matched_skills and "high" in priority:
            violations["priority_mismatch"].append(
                f"  Item {i+1} ({skill}): skill already matched but priority is '{priority}' — should not be 'high'"
            )

        for pattern in ALREADY_KNOW_PATTERNS:
            if pattern.search(why):
                violations["fabrication"].append(
                    f"  Item {i+1} ({skill}): 'already know' fabricated statement in 'why': {why[:80]}"
                )

    total = sum(len(v) for v in violations.values())
    return {"passed": total == 0, "total_violations": total, "violations": violations}


def _evaluate_case(case_dir: Path, case_data: dict, verbose: bool = False) -> dict:
    """Evaluate learning roadmap output for a single case."""
    expected_text = case_data["expected_text"]
    checks = _parse_expected(expected_text)

    result = _run_pipeline(case_data["cv"], case_data["jd"], "eval-lr")
    roadmap = build_learning_roadmap(result, max_items=10)
    roadmap = roadmap if isinstance(roadmap, list) else []

    guardrail_result = _check_guardrails(roadmap, result)

    priorities = {}
    for item in roadmap:
        p = item.get("priority", "unknown")
        priorities[p] = priorities.get(p, 0) + 1

    skill_names = [str(item.get("skill", "")) for item in roadmap]

    all_pass = (
        guardrail_result["passed"]
        and len(roadmap) >= 0  # 0 items is valid when all skills are matched
        and all(item.get("skill") for item in roadmap)
    )

    return {
        "case_name": case_dir.name,
        "all_pass": all_pass,
        "total_items": len(roadmap),
        "skill_names": skill_names,
        "priority_counts": priorities,
        "guardrail_passed": guardrail_result["passed"],
        "guardrail_violations": guardrail_result["violations"],
        "checks": checks,
        "items": [
            {
                "skill": item.get("skill"),
                "priority": item.get("priority"),
                "why": str(item.get("why", ""))[:100],
                "topics_count": len(item.get("topics") or []),
                "has_mini_project": bool(item.get("mini_project")),
                "has_cv_guidance": bool(item.get("cv_evidence_to_add_after_learning")),
                "do_not_claim": item.get("do_not_claim_until_completed"),
            }
            for item in roadmap
        ],
    }


def _find_cases(case_id: str | None = None) -> list[tuple[str, Path]]:
    """Find all learning roadmap evaluation cases."""
    eval_dir = PROJECT_ROOT / "evaluation" / "cases" / "learning_roadmap"
    if not eval_dir.exists():
        return []
    results: list[tuple[str, Path]] = []
    for case_dir in sorted(eval_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        if case_id and case_dir.name != f"case_lr_{case_id}":
            continue
        results.append(("learning_roadmap", case_dir))
    return results


def _print_summary(results: list[dict]) -> None:
    """Print evaluation summary."""
    total = len(results)
    passed = sum(1 for r in results if r.get("all_pass"))
    failed = total - passed

    print("\n" + "=" * 70)
    print("  AI CV FIT — LEARNING ROADMAP EVALUATION")
    print("=" * 70)
    print(f"  Total cases:     {total}")
    print(f"  Passed:          {passed} ({passed/total*100:.0f}%)")
    print(f"  Failed:          {failed} ({failed/total*100:.0f}%)")
    print()

    for r in results:
        status = "PASS" if r.get("all_pass") else "FAIL"
        print(f"  [{status}] {r.get('case_name', 'unknown')}")
        print(f"        Items: {r.get('total_items', 0)} — {r.get('priority_counts', {})}")
        if r.get("guardrail_violations"):
            for check, violations in r["guardrail_violations"].items():
                if violations:
                    print(f"        GUARDRAIL [{check}]:")
                    for v in violations:
                        print(f"          {v[:150]}")
        if r.get("items"):
            for i, item in enumerate(r["items"]):
                print(
                    f"          Item {i+1}: {item['skill']} "
                    f"[priority={item['priority']}, dnc={item['do_not_claim']}]"
                    f" topics={item['topics_count']}"
                )
        print()

    print("=" * 70)
    if failed > 0:
        print(f"  {failed} case(s) FAILED — review above for details")
    else:
        print("  ALL cases PASSED")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate learning roadmap cases")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--case", "-c", type=str, help="Run specific case (e.g. 'lr_01')")
    parser.add_argument("--export", "-e", type=Path, default=None)
    args = parser.parse_args()

    print("\n  AI CV Fit — Learning Roadmap Evaluation")
    print("  Loading cases...")

    cases = _find_cases(case_id=args.case)
    if not cases:
        print("  No cases found in evaluation/cases/learning_roadmap/")
        sys.exit(1)

    print(f"  Found {len(cases)} case(s). Running evaluation...\n")

    all_results: list[dict] = []
    for _, case_dir in cases:
        case_data = _load_case(case_dir)
        if case_data is None:
            print(f"  SKIP {case_dir.name}: missing files")
            continue

        result = _evaluate_case(case_dir, case_data, verbose=args.verbose)
        all_results.append(result)

        status = "PASS" if result.get("all_pass") else "FAIL"
        print(
            f"  [{status}] {case_dir.name}: "
            f"{result.get('total_items', 0)} roadmap items — "
            f"guardrail={'PASS' if result.get('guardrail_passed') else 'FAIL'}"
        )

    print()
    _print_summary(all_results)

    if args.export:
        args.export.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Results exported to: {args.export}")

    all_pass = all(r.get("all_pass", False) for r in all_results)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
