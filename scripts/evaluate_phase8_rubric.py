"""Deterministic multilingual Phase 8 rubric evaluation on synthetic fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.interview_realtime import summary_service  # noqa: E402


FIXTURES = BACKEND_ROOT / "tests" / "fixtures" / "phase8_rubric_evaluation.json"
VIETNAMESE_GUIDANCE_PREFIXES = (
    "Trả lời",
    "Bổ sung",
    "Dựa",
    "Dùng",
    "Giải thích",
    "Thay",
)


def evaluate() -> dict[str, object]:
    cases = json.loads(FIXTURES.read_text(encoding="utf-8"))
    checks = {
        "determinism": 0,
        "score_bounds": 0,
        "semantic_expectations": 0,
        "language_consistency": 0,
    }
    failures: list[str] = []

    for case in cases:
        scores = [
            summary_service._score_turn(case["question"], case["answer"])
            for _ in range(5)
        ]
        score = scores[0]
        if all(item == score for item in scores[1:]):
            checks["determinism"] += 1
        else:
            failures.append(f"{case['id']}: nondeterministic score")

        if all(0 <= value <= 5 for value in score.values()):
            checks["score_bounds"] += 1
        else:
            failures.append(f"{case['id']}: score outside 0..5")

        tokens = summary_service._token_sequence(case["answer"])
        actual = {
            "action": bool(summary_service._matching_term_count(tokens, summary_service._ACTION_TERMS)),
            "result": bool(
                (result_terms := summary_service._matching_term_count(
                    tokens, summary_service._RESULT_TERMS
                ))
                or summary_service._quantified_result_count(
                    tokens, has_result_term=result_terms > 0
                )
            ),
            "technical": bool(summary_service._matching_term_count(tokens, summary_service._TECHNICAL_TERMS)),
            "unsupported_claim": bool(
                summary_service._matching_term_count(
                    tokens, summary_service._UNSUPPORTED_CLAIM_TERMS
                )
            ),
        }
        semantic_ok = all(actual[key] == case[key] for key in actual)
        semantic_ok = semantic_ok and score["evidence"] >= case.get("minimum_evidence", 0)
        semantic_ok = semantic_ok and score["risk"] >= case.get("minimum_risk", 0)
        semantic_ok = semantic_ok and score["relevance"] <= case.get("maximum_relevance", 5)
        if semantic_ok:
            checks["semantic_expectations"] += 1
        else:
            failures.append(
                f"{case['id']}: expected semantics differ "
                f"expected={{action:{case['action']},result:{case['result']},"
                f"technical:{case['technical']},unsupported:{case['unsupported_claim']}}} "
                f"actual={actual} score={score}"
            )

        recommendations = summary_service._turn_recommendations(score)
        if recommendations and all(
            isinstance(item, str)
            and item.strip()
            and item.startswith(VIETNAMESE_GUIDANCE_PREFIXES)
            for item in recommendations
        ):
            checks["language_consistency"] += 1
        else:
            failures.append(
                f"{case['id']}: recommendation is missing or not Vietnamese"
            )

    total = len(cases)
    rates = {key: round(value / total, 4) for key, value in checks.items()}
    thresholds = {
        "determinism": 1.0,
        "score_bounds": 1.0,
        "semantic_expectations": 0.95,
        "language_consistency": 1.0,
    }
    passed = not failures and all(rates[key] >= threshold for key, threshold in thresholds.items())
    return {
        "evaluator_version": summary_service.EVALUATOR_VERSION,
        "fixture_count": total,
        "languages": sorted({case["language"] for case in cases}),
        "domains": sorted({case["domain"] for case in cases}),
        "rates": rates,
        "thresholds": thresholds,
        "failures": failures,
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = evaluate()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if args.check and not result["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
