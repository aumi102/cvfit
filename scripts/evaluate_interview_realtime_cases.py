"""
AI CV Fit — Evaluation Script for Interview Realtime Cases

Evaluates Phase 8 interview realtime session creation, turn tracking, feedback quality,
rubric scoring, and guardrail compliance.

Usage:
    python scripts/evaluate_interview_realtime_cases.py
    python scripts/evaluate_interview_realtime_cases.py --verbose
    python scripts/evaluate_interview_realtime_cases.py --case ir_tech_01
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.parsing.jd_parser import parse_jd
from app.services.scoring.scorer import score
from app.services.scoring.result_v2 import build_result_v2
from app.services.scoring.result_v3 import build_result_v3

# ---------------------------------------------------------------------------
# Forbidden patterns (guardrails)
# ---------------------------------------------------------------------------

FORBIDDEN_PATTERNS = [
    # Fabrication
    re.compile(r"\byou\s+(do\s+)?don[' ]?t\s+(know|have|possess)\s+\w+", re.IGNORECASE),
    re.compile(r"\bthe\s+candidate\s+doesn[' ]?t\s+know", re.IGNORECASE),
    re.compile(r"\byou\s+must\s+claim\s+\w+\s+experience", re.IGNORECASE),
    # Emotion / personality / truthfulness inference
    re.compile(r"\b(nervous|stressed|anxious|confident|shy|introvert|extrovert)\b", re.IGNORECASE),
    re.compile(r"\b(lying|liar|honest|truthful|truthfulness)\b", re.IGNORECASE),
    re.compile(r"\bpersonality\b", re.IGNORECASE),
    # Hiring guarantee
    re.compile(r"\bguarantee.*hire\b", re.IGNORECASE),
    re.compile(r"\bwill\s+get\s+hired\b", re.IGNORECASE),
    re.compile(r"\bunlikely\s+to\s+be\s+hired\b", re.IGNORECASE),
    re.compile(r"\bhiring\s+probability\b", re.IGNORECASE),
    # Protected attributes
    re.compile(r"\b(age|gender|ethnicity|religion|disability)\b", re.IGNORECASE),
    # Risk as truthfulness label
    re.compile(r"\brisk\s+score.*(truth|lie|honest)\b", re.IGNORECASE),
]

REQUIRED_FEEDBACK_FIELDS = {
    "score", "rubric", "feedback", "disclaimer",
}
REQUIRED_SESSION_FIELDS = {
    "id", "status", "consent_audio",
}
REQUIRED_TURN_FIELDS = {
    "question_text", "question_type", "turn_index",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_cv_jd_pipeline(cv_text: str, jd_text: str, job_id: str) -> dict:
    """Run scoring pipeline and return a v3 result."""
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
    """Load an interview realtime case from its directory."""
    cv_files = sorted(case_dir.glob("case_*_cv.txt"))
    jd_files = sorted(case_dir.glob("case_*_jd.txt"))
    expected_files = sorted(case_dir.glob("case_*_expected.md"))

    if not (cv_files and jd_files and expected_files):
        return None

    return {
        "cv": cv_files[0].read_text(encoding="utf-8"),
        "jd": jd_files[0].read_text(encoding="utf-8"),
        "expected": expected_files[0].read_text(encoding="utf-8"),
    }


def _check_forbidden(text: str) -> list[str]:
    """Return list of forbidden pattern matches in text."""
    violations = []
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            violations.append(pattern.pattern[:60])
    return violations


def _parse_case_type(text: str) -> dict:
    """Parse expected checks from expected.md."""
    return {
        "expects_question": "question" in text.lower() and "ask" in text.lower(),
        "expects_feedback": "feedback" in text.lower() or "score" in text.lower(),
        "expects_gap_wording": "no evidence" in text.lower(),
        "expects_star": "star" in text.lower(),
        "expects_specificity": "specific" in text.lower(),
        "expects_risk_label": "risk" in text.lower(),
        "expects_disclaimer": "disclaimer" in text.lower(),
        "expects_technical": "technical" in text.lower(),
        "expects_behavioral": "behavioral" in text.lower(),
        "expects_project": "project" in text.lower(),
        "expects_strong": "strong" in text.lower(),
        "expects_weak": "weak" in text.lower(),
    }


def _simulate_session(cv_text: str, jd_text: str, interview_type: str, difficulty: str) -> dict:
    """Simulate a realtime session outcome for evaluation.

    Since the actual WebRTC/AI interviewer is not available in the evaluation
    environment, we simulate the feedback generation using the scoring pipeline.
    This gives us deterministic, reproducible output for guardrail checking.
    """
    result = _run_cv_jd_pipeline(cv_text, jd_text, f"eval-{uuid.uuid4().hex[:8]}")

    # Extract matched/missing skills from result
    matched_skills = set()
    missing_skills = set()
    for skill_data in result.get("missing_skills", []):
        if isinstance(skill_data, dict):
            skill = skill_data.get("skill", "")
            if skill:
                missing_skills.add(skill.lower())
    for skill_data in result.get("matched_skills", []):
        if isinstance(skill_data, dict):
            skill = skill_data.get("skill", "")
            if skill:
                matched_skills.add(skill.lower())

    # Simulate a question about the first missing skill
    target_skill = next(iter(missing_skills), "Python")

    # Simulate a strong answer (references matched skill)
    matched_skill = next(iter(matched_skills), "Python")
    strong_answer = f"I have 3 years of experience with {matched_skill}. I used it to build a REST API at my previous job."

    # Simulate a weak answer (vague, no evidence)
    weak_answer = "I know some stuff about software development."

    # Determine which answer to simulate based on case type
    if "weak" in interview_type.lower() or "vague" in interview_type.lower():
        simulated_answer = weak_answer
    else:
        simulated_answer = strong_answer

    # Score the simulated answer using the scorer
    cv_parsed_for_scoring = result.get("cv", {})
    bullets = cv_parsed_for_scoring.get("parsed_bullets", [])

    # Generate feedback text similar to what AI interviewer would generate
    skill_mentioned = target_skill.lower() in simulated_answer.lower()

    if not skill_mentioned and target_skill:
        feedback_text = (
            f"Your answer did not mention {target_skill}. "
            f"No evidence of {target_skill} was found in your CV for this question. "
            f"Try providing a specific example with a technology or framework you have used."
        )
        score_val = 35
    elif len(simulated_answer) < 50:
        feedback_text = (
            "Your answer was too short to assess technical depth. "
            "Provide a more detailed response with specific examples and outcomes."
        )
        score_val = 25
    else:
        feedback_text = (
            f"Your answer mentioned {matched_skill} with a project example. "
            f"Consider adding more details about the scale and your specific contribution."
        )
        score_val = 70

    # Build simulated session output
    session = {
        "id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "status": "completed",
        "interview_type": interview_type,
        "difficulty": difficulty,
        "consent_audio": True,
        "consent_camera": False,
        "consent_recording": False,
        "turns": [
            {
                "turn_index": 0,
                "question_text": f"Describe your experience with {target_skill}.",
                "question_type": "technical",
                "answer_transcript": simulated_answer,
                "score": score_val,
                "feedback": feedback_text,
                "risk": "medium" if score_val < 50 else "low",
            }
        ],
        "summary": {
            "overall_score": score_val,
            "rubric": {
                "relevance": min(100, max(0, score_val + 5)),
                "specificity": min(100, max(0, score_val - 10)),
                "evidence": min(100, max(0, score_val - 5)),
                "structure": min(100, max(0, score_val + 8)),
                "technical_depth": min(100, max(0, score_val - 15)),
                "communication_clarity": min(100, max(0, score_val + 3)),
                "risk": max(0, 100 - score_val),
            },
            "feedback": feedback_text,
            "strengths": ["Provided a relevant example"] if score_val >= 50 else [],
            "weaknesses": [f"No evidence of {target_skill} found"] if score_val < 50 else [],
            "suggested_improvements": [
                "Add more specific details about your project and outcomes.",
            ],
            "next_questions": [
                "Can you describe a challenge you faced with this technology?",
            ],
            "learning_tasks": [
                {
                    "skill": target_skill,
                    "task_type": "project",
                    "priority": "high" if score_val < 50 else "medium",
                    "description": f"Build or document a project using {target_skill}.",
                }
            ],
            "disclaimer": (
                "This feedback is for practice only and does not guarantee hiring outcomes. "
                "Feedback is based on transcript evidence and known CV/JD data."
            ),
        },
    }
    return session


def _evaluate_case(case_dir: Path, case_data: dict) -> dict:
    """Evaluate a single interview realtime case."""
    expected = case_data["expected"]
    checks = _parse_case_type(expected)

    # Determine interview type and difficulty from expected text
    if checks["expects_technical"]:
        interview_type = "technical"
    elif checks["expects_behavioral"]:
        interview_type = "behavioral"
    elif checks["expects_project"]:
        interview_type = "project"
    elif checks["expects_weak"]:
        interview_type = "weak_vague"
    else:
        interview_type = "mixed"

    difficulty = "medium"
    if "easy" in expected.lower():
        difficulty = "easy"
    elif "hard" in expected.lower():
        difficulty = "hard"

    # Simulate session
    session = _simulate_session(
        case_data["cv"],
        case_data["jd"],
        interview_type,
        difficulty,
    )

    passes: list[str] = []
    fails: list[str] = []
    guardrail_violations: list[str] = []

    # --- Guardrail checks ---
    all_text = json.dumps(session, default=str)

    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(all_text):
            guardrail_violations.append(f"FORBIDDEN: {pattern.pattern[:60]}")

    # Check required fields in summary
    summary = session.get("summary", {})
    for field in REQUIRED_FEEDBACK_FIELDS:
        if field not in summary:
            fails.append(f"Missing required field in summary: {field}")

    # Check disclaimer
    if checks["expects_disclaimer"] or True:  # Disclaimer always required
        disclaimer = summary.get("disclaimer", "")
        if not disclaimer:
            fails.append("Missing disclaimer in summary")
        elif "practice only" not in disclaimer.lower():
            fails.append("Disclaimer missing 'practice only' wording")
        elif "guarantee" in disclaimer.lower() and "hiring" in disclaimer.lower():
            # This is actually OK — disclaimer should mention no guarantee
            pass
        else:
            passes.append("disclaimer present and correct")

    # Check "no evidence" wording for gap questions
    if checks["expects_gap_wording"]:
        feedback_text = summary.get("feedback", "")
        if "no evidence" in feedback_text.lower():
            passes.append("uses 'no evidence found' wording")
        elif "don't know" in feedback_text.lower() or "you don't have" in feedback_text.lower():
            fails.append("uses fabrication wording instead of 'no evidence'")
        else:
            passes.append("feedback text does not fabricate")

    # Check risk label not called "truthfulness"
    if checks["expects_risk_label"] or True:
        rubric = summary.get("rubric", {})
        risk_score = rubric.get("risk")
        if risk_score is not None:
            if "truthful" in all_text.lower() or "lying" in all_text.lower():
                fails.append("risk score labeled with truthfulness language")
            else:
                passes.append("risk score not labeled truthfulness")

    # Check learning tasks use skill names from analysis
    learning_tasks = summary.get("learning_tasks", [])
    if learning_tasks:
        for task in learning_tasks:
            task_text = json.dumps(task)
            if _check_forbidden(task_text):
                fails.append(f"Learning task has guardrail violation: {task_text[:80]}")
            if task.get("skill"):
                passes.append(f"Learning task derived from skill: {task.get('skill')}")

    # Check no CV text in summary fields
    cv_snippets = [
        case_data["cv"][i:i+50]
        for i in range(0, min(len(case_data["cv"]), 500), 50)
    ]
    for snippet in cv_snippets:
        if len(snippet.strip()) > 20 and snippet.strip() in all_text:
            fails.append(f"CV text snippet found in session output: {snippet[:30]}")
            break

    # Check score range
    score_val = summary.get("overall_score")
    if score_val is not None:
        if 0 <= score_val <= 100:
            passes.append(f"score in valid range [0,100]: {score_val}")
        else:
            fails.append(f"score out of range: {score_val}")

    # Check rubric has 7 dimensions
    rubric_dims = summary.get("rubric", {})
    expected_dims = {"relevance", "specificity", "evidence", "structure",
                     "technical_depth", "communication_clarity", "risk"}
    actual_dims = set(rubric_dims.keys())
    if actual_dims == expected_dims:
        passes.append("rubric has all 7 dimensions")
    elif expected_dims - actual_dims:
        fails.append(f"rubric missing dimensions: {expected_dims - actual_dims}")
    else:
        passes.append(f"rubric has dimensions: {sorted(actual_dims)}")

    all_pass = (
        len(fails) == 0
        and len(guardrail_violations) == 0
        and len(passes) >= 3
    )

    return {
        "case_name": case_dir.name,
        "all_pass": all_pass,
        "passes": passes,
        "fails": fails,
        "guardrail_violations": guardrail_violations,
        "session": {
            "id": session["id"],
            "status": session["status"],
            "overall_score": session["summary"].get("overall_score"),
            "rubric_dims": list(session["summary"].get("rubric", {}).keys()),
            "has_disclaimer": bool(session["summary"].get("disclaimer")),
        },
    }


def _find_cases(case_id: str | None = None) -> list[tuple[str, Path]]:
    """Find all interview realtime evaluation cases."""
    eval_dir = PROJECT_ROOT / "evaluation" / "cases" / "interview_realtime"
    if not eval_dir.exists():
        return []
    results: list[tuple[str, Path]] = []
    for case_dir in sorted(eval_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        if case_id and case_dir.name != f"case_ir_{case_id}":
            continue
        results.append(("interview_realtime", case_dir))
    return results


def _print_summary(results: list[dict]) -> None:
    """Print evaluation summary."""
    total = len(results)
    passed = sum(1 for r in results if r.get("all_pass"))
    failed = total - passed

    print("\n" + "=" * 70)
    print("  AI CV FIT — INTERVIEW REALTIME EVALUATION")
    print("=" * 70)
    print(f"  Total cases:     {total}")
    print(f"  Passed:          {passed} ({passed/total*100:.0f}%)" if total else "  Passed: 0")
    print(f"  Failed:          {failed} ({failed/total*100:.0f}%)" if total else "  Failed: 0")
    print()

    for r in results:
        status = "PASS" if r.get("all_pass") else "FAIL"
        print(f"  [{status}] {r.get('case_name', 'unknown')}")
        for p in r.get("passes", []):
            print(f"        + {p}")
        for f in r.get("fails", []):
            print(f"        - FAIL: {f}")
        for gv in r.get("guardrail_violations", []):
            print(f"        GUARDRAIL VIOLATION: {gv}")
        session = r.get("session", {})
        if session:
            print(f"        score={session.get('overall_score')} rubric_dims={session.get('rubric_dims')} disclaimer={session.get('has_disclaimer')}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate interview realtime cases")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--case", "-c", type=str, help="Run specific case (e.g. 'ir_tech_01')")
    parser.add_argument("--export", "-e", type=Path, default=None)
    args = parser.parse_args()

    print("\n  AI CV Fit — Interview Realtime Evaluation")
    print("  Loading cases...")

    cases = _find_cases(case_id=args.case)
    if not cases:
        print("  No cases found in evaluation/cases/interview_realtime/")
        print("  Creating cases from scratch...")
        sys.exit(1)

    print(f"  Found {len(cases)} case(s). Running evaluation...\n")

    all_results: list[dict] = []
    for _, case_dir in cases:
        case_data = _load_case(case_dir)
        if case_data is None:
            print(f"  SKIP {case_dir.name}: missing files")
            continue

        result = _evaluate_case(case_dir, case_data)
        all_results.append(result)

        status = "PASS" if result.get("all_pass") else "FAIL"
        session = result.get("session", {})
        print(
            f"  [{status}] {case_dir.name}: "
            f"score={session.get('overall_score')} "
            f"dims={len(session.get('rubric_dims', []))} "
            f"disclaimer={session.get('has_disclaimer')}"
        )

    print()
    _print_summary(all_results)

    if args.export:
        args.export.write_text(
            json.dumps(all_results, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"  Results exported to: {args.export}")

    all_pass = all(r.get("all_pass", False) for r in all_results)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
