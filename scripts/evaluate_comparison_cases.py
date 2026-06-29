"""
AI CV Fit — Evaluation Script for Before/After Comparison Cases

Evaluates the comparison engine (compare_results) on before/after CV pairs.

Usage:
    python scripts/evaluate_comparison_cases.py
    python scripts/evaluate_comparison_cases.py --verbose
    python scripts/evaluate_comparison_cases.py --case ba_01
    python scripts/evaluate_comparison_cases.py --category before_after
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
from app.services.comparison.compare_results import compare_results

COMPARISON_REQUIRED_KEYS = (
    "base_job_id",
    "new_job_id",
    "base_score",
    "new_score",
    "score_delta",
    "breakdown_delta",
    "resolved_missing_skills",
    "still_missing_skills",
    "newly_matched_skills",
    "new_evidence",
    "keyword_stuffing_warnings",
    "improvement_summary",
    "next_actions",
)

GUARANTEE_PATTERNS = [
    re.compile(r"\bguarantee[sd]?\s+(an?\s+)?(interview|job|hired)", re.IGNORECASE),
    re.compile(r"\bwill\s+definitely\s+(get\s+)?(hired|selected)", re.IGNORECASE),
    re.compile(r"\byou\s+will\s+(definitely\s+)?(get\s+)?(the\s+)?job", re.IGNORECASE),
    re.compile(r"guaranteed\s+(to\s+)?(get\s+)?(hired|interview)", re.IGNORECASE),
]

FABRICATE_PATTERNS = [
    re.compile(r"\byou\s+(do\s+)?don[' ]?t\s+(know|have|possess)\s+\w+", re.IGNORECASE),
    re.compile(r"\b(no|zero)\s+(experience|knowledge)\s+in\s+\w+", re.IGNORECASE),
]


def _run_pipeline(cv_text: str, jd_text: str, job_id: str) -> dict:
    """Run the full scoring pipeline on a CV/JD pair and return a v3 result."""
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
    """Load a before/after case from its directory.

    Discovers the case prefix by globbing for the first matching file.
    This allows any naming convention (case_ba_01, case_ba_02, etc.) to work.
    """
    # Discover prefix by globbing for the first matching file
    cv_files = sorted(case_dir.glob("case_*_cv.txt"))
    jd_files = sorted(case_dir.glob("case_*_jd.txt"))
    expected_files = sorted(case_dir.glob("case_*_expected.md"))
    revised_files = sorted(case_dir.glob("case_*_revised.txt"))

    if not (cv_files and jd_files and expected_files and revised_files):
        return None

    cv_file = cv_files[0]
    jd_file = jd_files[0]
    revised_file = revised_files[0]
    expected_file = expected_files[0]

    # Extract prefix from the discovered filename (e.g. "case_ba_01" from "case_ba_01_cv.txt")
    prefix = cv_file.stem.replace("_cv", "")

    return {
        "base_cv": cv_file.read_text(encoding="utf-8"),
        "jd": jd_file.read_text(encoding="utf-8"),
        "revised_cv": revised_file.read_text(encoding="utf-8"),
        "expected_text": expected_file.read_text(encoding="utf-8"),
    }


def _parse_score_range(text: str, prefix: str) -> tuple[float, float]:
    """Parse expected score range for base or new score."""
    patterns = [
        rf"{prefix}_score:\s*(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)",
        rf"{prefix}_score:\s*(\d+(?:\.\d+)?)\s*\(.*?\)",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            low = float(m.group(1))
            high = float(m.group(2) if m.lastindex and m.group(2) else m.group(1))
            return (low, high)
    return (0.0, 100.0)


def _parse_delta_range(text: str) -> tuple[float, float]:
    """Parse expected score_delta range."""
    patterns = [
        r"score_delta:\s*([+-]?\d+(?:\.\d+)?)\s*[-–to]+\s*([+-]?\d+(?:\.\d+)?)",
        r"score_delta:\s*([+-]?\d+(?:\.\d+)?)\s*\(",
    ]
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            low = float(m.group(1))
            high = float(m.group(2) if m.lastindex and m.group(2) else m.group(1))
            return (low, high)
    return (-100.0, 100.0)


def _check_guardrails(comparison: dict, base_score: float, new_score: float) -> dict:
    """Run guardrail checks on the comparison output."""
    violations: dict[str, list[str]] = {
        "guarantee": [],
        "fabrication": [],
        "score_delta_direction": [],
    }

    all_text = json.dumps(comparison, default=str).lower()
    for pattern in GUARANTEE_PATTERNS:
        if pattern.search(all_text):
            violations["guarantee"].append(f"  Guarantee pattern: {pattern.pattern[:60]}")

    for pattern in FABRICATE_PATTERNS:
        if pattern.search(all_text):
            violations["fabrication"].append(f"  Fabricate pattern: {pattern.pattern[:60]}")

    delta = comparison.get("score_delta")
    if delta is not None:
        unresolved = len(comparison.get("keyword_stuffing_warnings") or [])
        resolved = len(comparison.get("resolved_missing_skills") or [])
        if unresolved > 0 and delta > 15:
            violations["score_delta_direction"].append(
                f"  keyword_stuffing_warnings={unresolved} but score_delta={delta} — stuffing should not improve score significantly"
            )

    total = sum(len(v) for v in violations.values())
    return {"passed": total == 0, "total_violations": total, "violations": violations}


def _evaluate_case(case_dir: Path, case_data: dict, verbose: bool = False) -> dict:
    """Run comparison on a single case and evaluate against expected behavior."""
    expected = case_data["expected_text"]
    base_range = _parse_score_range(expected, "base")
    new_range = _parse_score_range(expected, "new")
    delta_range = _parse_delta_range(expected)

    base_result = _run_pipeline(case_data["base_cv"], case_data["jd"], "eval-base")
    new_result = _run_pipeline(case_data["revised_cv"], case_data["jd"], "eval-new")

    comparison = compare_results(
        base_result,
        new_result,
        base_job_id="eval-base",
        new_job_id="eval-new",
    )

    missing_keys = [k for k in COMPARISON_REQUIRED_KEYS if k not in comparison]
    if missing_keys:
        return {
            "case_name": case_dir.name,
            "all_pass": False,
            "error": f"Missing keys: {missing_keys}",
        }

    base_score = comparison.get("base_score") or 0.0
    new_score = comparison.get("new_score") or 0.0
    delta = comparison.get("score_delta")

    base_ok = base_range[0] <= base_score <= base_range[1]
    new_ok = new_range[0] <= new_score <= new_range[1]
    delta_ok = delta_range[0] <= (delta or 0) <= delta_range[1]

    guardrail_result = _check_guardrails(comparison, base_score, new_score)

    all_pass = base_ok and new_ok and delta_ok and guardrail_result["passed"] and not missing_keys

    return {
        "case_name": case_dir.name,
        "all_pass": all_pass,
        "base_score": base_score,
        "new_score": new_score,
        "score_delta": delta,
        "base_range": base_range,
        "new_range": new_range,
        "delta_range": delta_range,
        "base_ok": base_ok,
        "new_ok": new_ok,
        "delta_ok": delta_ok,
        "guardrail_passed": guardrail_result["passed"],
        "guardrail_violations": guardrail_result["violations"],
        "resolved_count": len(comparison.get("resolved_missing_skills") or []),
        "still_missing_count": len(comparison.get("still_missing_skills") or []),
        "newly_matched_count": len(comparison.get("newly_matched_skills") or []),
        "keyword_stuffing_count": len(comparison.get("keyword_stuffing_warnings") or []),
        "improvement_summary": comparison.get("improvement_summary", ""),
    }


def _find_cases(category: str | None = None, case_id: str | None = None) -> list[tuple[str, Path]]:
    """Find all before/after evaluation cases."""
    eval_dir = PROJECT_ROOT / "evaluation" / "cases" / "before_after"
    if not eval_dir.exists():
        return []
    results: list[tuple[str, Path]] = []
    for case_dir in sorted(eval_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        if case_id and case_dir.name != f"case_ba_{case_id}":
            continue
        results.append(("before_after", case_dir))
    return results


def _print_summary(results: list[dict]) -> None:
    """Print evaluation summary."""
    total = len(results)
    passed = sum(1 for r in results if r.get("all_pass"))
    failed = total - passed

    print("\n" + "=" * 70)
    print("  AI CV FIT — BEFORE/AFTER COMPARISON EVALUATION")
    print("=" * 70)
    print(f"  Total cases:     {total}")
    print(f"  Passed:          {passed} ({passed/total*100:.0f}%)")
    print(f"  Failed:          {failed} ({failed/total*100:.0f}%)")
    print()

    for r in results:
        status = "PASS" if r.get("all_pass") else "FAIL"
        print(f"  [{status}] {r.get('case_name', 'unknown')}")
        if "error" in r:
            print(f"        ERROR: {r['error']}")
            continue
        print(f"        Base: {r.get('base_score', '?')} (range {r['base_range']}) {'OK' if r.get('base_ok') else 'FAIL'}")
        print(f"        New:  {r.get('new_score', '?')} (range {r['new_range']}) {'OK' if r.get('new_ok') else 'FAIL'}")
        print(f"        Delta: {r.get('score_delta', '?')} (range {r['delta_range']}) {'OK' if r.get('delta_ok') else 'FAIL'}")
        print(f"        Guardrail: {'PASS' if r.get('guardrail_passed') else 'FAIL'}")
        print(f"        Resolved: {r.get('resolved_count', 0)}, Still missing: {r.get('still_missing_count', 0)}")
        print(f"        Newly matched: {r.get('newly_matched_count', 0)}, KS warnings: {r.get('keyword_stuffing_count', 0)}")
        if r.get("guardrail_violations"):
            for check, violations in r["guardrail_violations"].items():
                if violations:
                    print(f"        GUARDRAIL [{check}]:")
                    for v in violations:
                        print(f"          {v}")

    print("=" * 70)
    if failed > 0:
        print(f"  {failed} case(s) FAILED — review above for details")
    else:
        print("  ALL cases PASSED")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate before/after comparison cases")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--case", "-c", type=str, help="Run specific case (e.g. 'ba_01')")
    parser.add_argument("--export", "-e", type=Path, default=None)
    args = parser.parse_args()

    print("\n  AI CV Fit — Before/After Comparison Evaluation")
    print("  Loading cases...")

    cases = _find_cases(case_id=args.case)
    if not cases:
        print(f"  No cases found in evaluation/cases/before_after/")
        sys.exit(1)

    print(f"  Found {len(cases)} case(s). Running evaluation...\n")

    all_results: list[dict] = []
    for _, case_dir in cases:
        case_data = _load_case(case_dir)
        if case_data is None:
            print(f"  SKIP {case_dir.name}: missing required files")
            continue

        result = _evaluate_case(case_dir, case_data, verbose=args.verbose)
        all_results.append(result)

        status = "PASS" if result.get("all_pass") else "FAIL"
        if "error" in result:
            print(f"  [{status}] {case_dir.name}: {result['error']}")
        else:
            print(
                f"  [{status}] {case_dir.name}: "
                f"base={result.get('base_score')} new={result.get('new_score')} "
                f"delta={result.get('score_delta')} "
                f"ks={result.get('keyword_stuffing_count', 0)}"
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
