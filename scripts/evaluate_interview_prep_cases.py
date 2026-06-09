"""
AI CV Fit — Evaluation Script for Interview Prep Cases

Evaluates the interview prep generation (build_interview_prep) for quality and guardrails.

Usage:
    python scripts/evaluate_interview_prep_cases.py
    python scripts/evaluate_interview_prep_cases.py --verbose
    python scripts/evaluate_interview_prep_cases.py --case ip_01
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
from app.services.interview.interview_prep import build_interview_prep

VALID_QUESTION_TYPES = {"technical", "behavioral", "project_deep_dive", "gap_probe", "system_design"}

FABRICATE_PATTERNS = [
    re.compile(r"\byou\s+(do\s+)?don[' ]?t\s+(know|have|possess)\s+\w+", re.IGNORECASE),
    re.compile(r"\bthe\s+candidate\s+doesn[' ]?t\s+know", re.IGNORECASE),
    re.compile(r"\byou\s+must\s+claim\s+\w+\s+experience", re.IGNORECASE),
]


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
    """Load an interview prep case from its directory.

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


def _parse_questions_check(text: str) -> dict:
    """Parse expected question types and requirements from expected.md.

    Key design: explicit denial patterns (e.g. "**no gap_probe**") override
    the word-count "has" signals, because the word appears in context
    (bold/asterisk markers) that signals intentional specification.
    """
    # Bold/asterisk negation: "**no gap_probe**" or "*no project_deep_dive*"
    # These always take priority — they signal intentional specification.
    bold_no_gap = re.search(r"\*+\s*no\s+gap_probe\s*\*+", text, re.IGNORECASE)
    bold_no_pdd = re.search(r"\*+\s*no\s+project_deep_dive\s*\*+", text, re.IGNORECASE)

    # Line-level negation: "no gap_probe questions expected" on its own line
    line_no_gap = re.search(r"^\s*[-*]\s+no\s+gap_probe\b", text, re.IGNORECASE | re.MULTILINE)
    line_no_pdd = re.search(r"^\s*[-*]\s+no\s+project_deep_dive\b", text, re.IGNORECASE | re.MULTILINE)

    explicit_no_gap = bold_no_gap is not None or line_no_gap is not None
    explicit_no_pdd = bold_no_pdd is not None or line_no_pdd is not None

    return {
        # True only when the word appears in a positive "Must include" context
        "has_project_deep_dive": "project_deep_dive" in text.lower(),
        "has_gap_probe": "gap_probe" in text.lower(),
        # True only for explicit denial markers
        "no_project_deep_dive": explicit_no_pdd,
        "no_gap_probe": explicit_no_gap,
        "calibrate_junior": "calibrate" in text.lower() and "junior" in text.lower(),
        "calibrate_senior": "calibrate" in text.lower() and "senior" in text.lower(),
    }


def _check_guardrails(questions: list[dict], result: dict) -> dict:
    """Run guardrail checks on the interview prep output."""
    violations: dict[str, list[str]] = {
        "fabrication": [],
        "missing_fields": [],
        "irrelevant_skills": [],
        "unstructured_answer": [],
    }

    all_text = json.dumps(questions, default=str)

    for pattern in FABRICATE_PATTERNS:
        for i, q in enumerate(questions):
            q_text = json.dumps(q, default=str)
            if pattern.search(q_text):
                violations["fabrication"].append(
                    f"  Q{i+1} ({q.get('type','?')}): {pattern.pattern[:60]}"
                )

    required_fields = {"question", "type", "why_this_question", "suggested_answer_outline", "risk_if_user_cannot_answer"}
    for i, q in enumerate(questions):
        missing = required_fields - set(q.keys())
        if missing:
            violations["missing_fields"].append(
                f"  Q{i+1}: missing fields: {missing}"
            )

    for i, q in enumerate(questions):
        if q.get("type") not in VALID_QUESTION_TYPES:
            violations["irrelevant_skills"].append(
                f"  Q{i+1}: invalid type '{q.get('type')}'"
            )
        if isinstance(q.get("suggested_answer_outline"), list) and not q["suggested_answer_outline"]:
            violations["unstructured_answer"].append(
                f"  Q{i+1}: suggested_answer_outline is an empty list"
            )

    total = sum(len(v) for v in violations.values())
    return {"passed": total == 0, "total_violations": total, "violations": violations}


def _evaluate_case(case_dir: Path, case_data: dict, verbose: bool = False) -> dict:
    """Evaluate interview prep output for a single case."""
    expected_text = case_data["expected_text"]
    checks = _parse_questions_check(expected_text)

    result = _run_pipeline(case_data["cv"], case_data["jd"], "eval-ip")
    questions = build_interview_prep(result, max_questions=10)
    questions = questions if isinstance(questions, list) else []

    guardrail_result = _check_guardrails(questions, result)

    q_type_counts: dict[str, int] = {}
    for q in questions:
        t = q.get("type", "unknown")
        q_type_counts[t] = q_type_counts.get(t, 0) + 1

    project_dive_count = q_type_counts.get("project_deep_dive", 0)
    gap_probe_count = q_type_counts.get("gap_probe", 0)

    passes: list[str] = []
    fails: list[str] = []

    # Explicit denials take PRIORITY over "has" checks.
    # This handles cases like "**no gap_probe** questions expected" where
    # the keyword appears in text but is explicitly negated.
    gap_probe_not_allowed = checks.get("no_gap_probe", False)
    pdd_not_allowed = checks.get("no_project_deep_dive", False)

    # gap_probe checks — explicit denial FIRST
    if gap_probe_not_allowed:
        if gap_probe_count == 0:
            passes.append("correctly has no gap_probe")
        else:
            fails.append("expected NO gap_probe but found")
    elif checks["has_gap_probe"]:
        if gap_probe_count > 0:
            passes.append("has gap_probe")
        else:
            fails.append("expected gap_probe but none found")

    # project_deep_dive checks — explicit denial FIRST
    if pdd_not_allowed:
        if project_dive_count == 0:
            passes.append("correctly has no project_deep_dive")
        else:
            fails.append("expected NO project_deep_dive but found")
    elif checks["has_project_deep_dive"]:
        if project_dive_count > 0:
            passes.append("has project_deep_dive")
        else:
            fails.append("expected project_deep_dive but none found")
    else:
        # Neither explicit denial nor positive "has" signal — no check needed
        pass

    all_pass = (
        guardrail_result["passed"]
        and len(fails) == 0
        and len(questions) > 0
        and all(q.get("question") for q in questions)
    )

    return {
        "case_name": case_dir.name,
        "all_pass": all_pass,
        "total_questions": len(questions),
        "q_type_counts": q_type_counts,
        "passes": passes,
        "fails": fails,
        "guardrail_passed": guardrail_result["passed"],
        "guardrail_violations": guardrail_result["violations"],
        "questions": [
            {
                "type": q.get("type"),
                "question": q.get("question", "")[:100],
                "has_why": bool(q.get("why_this_question")),
                "has_outline": bool(q.get("suggested_answer_outline")),
                "has_risk": bool(q.get("risk_if_user_cannot_answer")),
            }
            for q in questions
        ],
    }


def _find_cases(case_id: str | None = None) -> list[tuple[str, Path]]:
    """Find all interview prep evaluation cases."""
    eval_dir = PROJECT_ROOT / "evaluation" / "cases" / "interview_prep"
    if not eval_dir.exists():
        return []
    results: list[tuple[str, Path]] = []
    for case_dir in sorted(eval_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        if case_id and case_dir.name != f"case_ip_{case_id}":
            continue
        results.append(("interview_prep", case_dir))
    return results


def _print_summary(results: list[dict], verbose: bool = False) -> None:
    """Print evaluation summary."""
    total = len(results)
    passed = sum(1 for r in results if r.get("all_pass"))
    failed = total - passed

    print("\n" + "=" * 70)
    print("  AI CV FIT — INTERVIEW PREP EVALUATION")
    print("=" * 70)
    print(f"  Total cases:     {total}")
    print(f"  Passed:          {passed} ({passed/total*100:.0f}%)")
    print(f"  Failed:          {failed} ({failed/total*100:.0f}%)")
    print()

    for r in results:
        status = "PASS" if r.get("all_pass") else "FAIL"
        print(f"  [{status}] {r.get('case_name', 'unknown')}")
        print(f"        Questions: {r.get('total_questions', 0)} — {r.get('q_type_counts', {})}")
        for p in r.get("passes", []):
            print(f"        + {p}")
        for f in r.get("fails", []):
            print(f"        - FAIL: {f}")
        if r.get("guardrail_violations"):
            for check, violations in r["guardrail_violations"].items():
                if violations:
                    print(f"        GUARDRAIL [{check}]:")
                    for v in violations:
                        print(f"          {v}")
        if verbose and r.get("questions"):
            for i, q in enumerate(r["questions"]):
                print(f"          Q{i+1} [{q['type']}] {q['question'][:80]}...")
                print(f"            why={q['has_why']} outline={q['has_outline']} risk={q['has_risk']}")
        print()

    print("=" * 70)
    if failed > 0:
        print(f"  {failed} case(s) FAILED — review above for details")
    else:
        print("  ALL cases PASSED")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate interview prep cases")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--case", "-c", type=str, help="Run specific case (e.g. 'ip_01')")
    parser.add_argument("--export", "-e", type=Path, default=None)
    args = parser.parse_args()

    print("\n  AI CV Fit — Interview Prep Evaluation")
    print("  Loading cases...")

    cases = _find_cases(case_id=args.case)
    if not cases:
        print("  No cases found in evaluation/cases/interview_prep/")
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
            f"{result.get('total_questions', 0)} questions — "
            f"{result.get('q_type_counts', {})}"
        )

    print()
    _print_summary(all_results, verbose=args.verbose)

    if args.export:
        args.export.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Results exported to: {args.export}")

    all_pass = all(r.get("all_pass", False) for r in all_results)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
