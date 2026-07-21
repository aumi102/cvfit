"""Server-side deterministic Phase 8 transcript evaluation and summaries."""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    InterviewRealtimeSession,
    InterviewRealtimeSummary,
    InterviewRealtimeTurn,
)


RUBRIC_VERSION = "realtime_practice_v1"
EVALUATOR_VERSION = "deterministic_transcript_v1"
TRANSCRIPT_PROVENANCE = "client_reported_validated"
SUMMARY_DISCLAIMER = (
    "AI interview feedback is for practice only and does not predict hiring outcomes."
)

RUBRIC_DIMENSIONS = (
    "relevance",
    "specificity",
    "evidence",
    "structure",
    "technical_depth",
    "communication_clarity",
    "risk",
)
POSITIVE_DIMENSIONS = RUBRIC_DIMENSIONS[:-1]

_DIMENSION_LABELS = {
    "relevance": "job relevance",
    "specificity": "specific detail",
    "evidence": "evidence grounding",
    "structure": "answer structure",
    "technical_depth": "technical depth",
    "communication_clarity": "communication clarity",
    "risk": "unsupported-claim risk",
}
_TECHNICAL_TERMS = {
    "api",
    "architecture",
    "backend",
    "cache",
    "database",
    "deploy",
    "design",
    "framework",
    "latency",
    "migration",
    "performance",
    "query",
    "security",
    "service",
    "testing",
}
_ACTION_TERMS = {
    "built",
    "created",
    "designed",
    "implemented",
    "improved",
    "led",
    "migrated",
    "optimized",
    "resolved",
    "tested",
}
_RESULT_TERMS = {
    "delivered",
    "improved",
    "increased",
    "reduced",
    "result",
    "saved",
    "success",
}
_STRUCTURE_TERMS = {"situation", "task", "action", "result", "first", "then", "finally"}
_UNSUPPORTED_CLAIM_TERMS = {
    "always",
    "best",
    "expert",
    "guarantee",
    "never fail",
    "perfect",
    "100%",
}


def generate_deterministic_summary_if_ready(
    db: Session,
    session: InterviewRealtimeSession,
) -> InterviewRealtimeSummary | None:
    """Evaluate validated client-reported turns and persist a versioned summary.

    Transcript text is not treated as provider-authenticated evidence. The
    evaluator is a bounded, deterministic practice heuristic owned by the
    backend; it never infers emotion, personality, honesty, or hiring outcome.
    """
    turns = (
        db.query(InterviewRealtimeTurn)
        .filter(InterviewRealtimeTurn.session_id == session.id)
        .order_by(InterviewRealtimeTurn.turn_index.asc())
        .all()
    )
    if not turns:
        return None

    existing = _get_summary(db, session.id)
    if existing is not None and summary_status(existing) == "ready":
        return existing

    try:
        scores = [_trusted_or_deterministic_score(turn) for turn in turns]
        return _persist_ready_summary(db, session, turns, scores, existing=existing)
    except Exception:
        # Do not leak transcript content or internal exception details. A repeat
        # completion request can retry this deterministic operation safely.
        return _persist_failed_summary(db, session, existing=existing)


def summary_status(summary: InterviewRealtimeSummary | None) -> str:
    if summary is None or not isinstance(summary.rubric_json, dict):
        return "pending"
    value = summary.rubric_json.get("status")
    return value if value in {"ready", "failed"} else "pending"


def summary_rubric_version(summary: InterviewRealtimeSummary | None) -> str | None:
    if summary is None or not isinstance(summary.rubric_json, dict):
        return None
    value = summary.rubric_json.get("rubric_version")
    return value if isinstance(value, str) and value else None


def summary_failure_code(summary: InterviewRealtimeSummary | None) -> str | None:
    if summary_status(summary) != "failed" or summary is None:
        return None
    value = summary.rubric_json.get("failure_code")
    return value if isinstance(value, str) and value else "summary_generation_failed"


def _trusted_or_deterministic_score(turn: InterviewRealtimeTurn) -> dict[str, float]:
    trusted = _validated_trusted_score(turn.score_json)
    if trusted is not None:
        return trusted

    score = _score_turn(turn.question_text, turn.answer_transcript)
    turn.score_json = {
        **score,
        "_meta": {
            "source": "server_deterministic",
            "evaluator_version": EVALUATOR_VERSION,
            "rubric_version": RUBRIC_VERSION,
            "transcript_provenance": TRANSCRIPT_PROVENANCE,
        },
    }
    turn.feedback_json = {
        "source": "server_deterministic",
        "evaluator_version": EVALUATOR_VERSION,
        "rubric_version": RUBRIC_VERSION,
        "transcript_provenance": TRANSCRIPT_PROVENANCE,
        "recommendations": _turn_recommendations(score),
        "limitations": [
            "The transcript was reported by the browser and was not cryptographically verified by the provider.",
            SUMMARY_DISCLAIMER,
        ],
    }
    return score


def _score_turn(question_text: str | None, answer_text: str | None) -> dict[str, float]:
    question_tokens = _tokens(question_text)
    answer_tokens = _tokens(answer_text)
    word_count = len(answer_tokens)
    if word_count == 0:
        return {
            "relevance": 0.5,
            "specificity": 0.0,
            "evidence": 0.0,
            "structure": 0.0,
            "technical_depth": 0.0,
            "communication_clarity": 0.5,
            "risk": 3.5,
        }

    overlap = len(question_tokens & answer_tokens) / max(1, len(question_tokens))
    length_factor = min(word_count / 80, 1.0)
    digit_count = sum(token.isdigit() or any(char.isdigit() for char in token) for token in answer_tokens)
    action_count = len(answer_tokens & _ACTION_TERMS)
    result_count = len(answer_tokens & _RESULT_TERMS)
    structure_count = len(answer_tokens & _STRUCTURE_TERMS)
    technical_count = len(answer_tokens & _TECHNICAL_TERMS)
    first_person = bool(answer_tokens & {"i", "my", "we", "our"})
    normalized_answer = " ".join(answer_tokens)
    unsupported_count = sum(term in normalized_answer for term in _UNSUPPORTED_CLAIM_TERMS)

    relevance = _bounded(1.0 + (overlap * 2.5) + (length_factor * 1.5))
    specificity = _bounded(0.8 + (length_factor * 2.0) + min(digit_count, 2) * 0.5 + min(technical_count, 3) * 0.25)
    evidence = _bounded(0.5 + (1.0 if first_person else 0.0) + min(action_count, 2) * 0.8 + min(result_count + digit_count, 2) * 0.7)
    structure = _bounded(0.8 + (length_factor * 1.5) + min(structure_count, 4) * 0.6)
    technical_depth = _bounded(0.5 + (length_factor * 1.5) + min(technical_count, 5) * 0.55)

    sentence_lengths = [
        len(_tokens(sentence))
        for sentence in re.split(r"[.!?]+", answer_text or "")
        if _tokens(sentence)
    ]
    average_sentence = sum(sentence_lengths) / max(1, len(sentence_lengths))
    clarity_penalty = 0.8 if average_sentence > 45 else 0.0
    communication_clarity = _bounded(1.5 + (length_factor * 2.0) - clarity_penalty)

    evidence_gap = 1.0 if evidence < 2.0 and word_count >= 20 else 0.0
    risk = _bounded(0.5 + unsupported_count * 1.0 + evidence_gap)
    return {
        "relevance": relevance,
        "specificity": specificity,
        "evidence": evidence,
        "structure": structure,
        "technical_depth": technical_depth,
        "communication_clarity": communication_clarity,
        "risk": risk,
    }


def _persist_ready_summary(
    db: Session,
    session: InterviewRealtimeSession,
    turns: list[InterviewRealtimeTurn],
    scores: list[dict[str, float]],
    *,
    existing: InterviewRealtimeSummary | None,
) -> InterviewRealtimeSummary:
    averages = {
        dimension: round(sum(score[dimension] for score in scores) / len(scores), 2)
        for dimension in RUBRIC_DIMENSIONS
    }
    positive_average = sum(averages[dimension] for dimension in POSITIVE_DIMENSIONS) / len(
        POSITIVE_DIMENSIONS
    )
    overall_score = round(((positive_average * 0.85) + ((5 - averages["risk"]) * 0.15)) * 20)
    overall_score = max(0, min(100, overall_score))

    strengths = [
        f"Consistent {_DIMENSION_LABELS[dimension]}."
        for dimension in POSITIVE_DIMENSIONS
        if averages[dimension] >= 3.5
    ]
    weaknesses = [
        f"Needs more {_DIMENSION_LABELS[dimension]}."
        for dimension in POSITIVE_DIMENSIONS
        if averages[dimension] < 2.5
    ]
    if averages["risk"] >= 2.5:
        weaknesses.append("Some answers contain unsupported-claim risk signals.")

    weakest_dimensions = sorted(POSITIVE_DIMENSIONS, key=averages.get)[:2]
    improvements = [_improvement_for(dimension) for dimension in weakest_dimensions]
    if averages["risk"] >= 2.5:
        improvements.append(
            "Separate verified experience from skills still being learned and avoid absolute claims."
        )

    evidence_ids = [str(turn.id) for turn in turns]
    rubric = {
        "status": "ready",
        "rubric_version": RUBRIC_VERSION,
        "evaluator_version": EVALUATOR_VERSION,
        "transcript_provenance": TRANSCRIPT_PROVENANCE,
        "dimensions": {
            dimension: {
                "score": averages[dimension],
                "max_score": 5.0,
                "evidence_turn_ids": evidence_ids,
            }
            for dimension in RUBRIC_DIMENSIONS
        },
    }
    learning_tasks = [
        {
            "task_type": "interview_prep",
            "priority": "high" if averages[dimension] < 2 else "medium",
            "title": f"Improve {_DIMENSION_LABELS[dimension]}",
            "description": _improvement_for(dimension),
            "source": "realtime_interview_summary",
            "rubric_version": RUBRIC_VERSION,
        }
        for dimension in weakest_dimensions
    ]
    limitations = [
        "The transcript was reported by the browser and was not cryptographically verified by the provider.",
        "This deterministic practice rubric uses bounded text heuristics and requires independent quality evaluation.",
        "It does not evaluate emotion, facial expression, personality, truthfulness, protected attributes, or hiring probability.",
        SUMMARY_DISCLAIMER,
    ]

    summary = existing or _new_summary(session.id)
    if existing is None:
        db.add(summary)
    now = datetime.utcnow()
    summary.overall_score = overall_score
    summary.rubric_json = rubric
    summary.strengths_json = strengths
    summary.weaknesses_json = weaknesses
    summary.suggested_improvements_json = improvements
    summary.next_questions_json = [
        f"Practice one job-relevant answer focused on {_DIMENSION_LABELS[dimension]}."
        for dimension in weakest_dimensions
    ]
    summary.learning_tasks_json = learning_tasks
    summary.limitations_json = limitations
    summary.updated_at = now
    return summary


def _persist_failed_summary(
    db: Session,
    session: InterviewRealtimeSession,
    *,
    existing: InterviewRealtimeSummary | None,
) -> InterviewRealtimeSummary:
    summary = existing or _new_summary(session.id)
    if existing is None:
        db.add(summary)
    summary.overall_score = None
    summary.rubric_json = {
        "status": "failed",
        "rubric_version": RUBRIC_VERSION,
        "evaluator_version": EVALUATOR_VERSION,
        "failure_code": "summary_generation_failed",
        "dimensions": {},
    }
    summary.strengths_json = []
    summary.weaknesses_json = []
    summary.suggested_improvements_json = []
    summary.next_questions_json = []
    summary.learning_tasks_json = []
    summary.limitations_json = [
        "Summary generation failed safely; persisted transcript turns were retained for retry.",
        SUMMARY_DISCLAIMER,
    ]
    summary.updated_at = datetime.utcnow()
    return summary


def _new_summary(session_id: uuid.UUID) -> InterviewRealtimeSummary:
    now = datetime.utcnow()
    return InterviewRealtimeSummary(
        id=uuid.uuid4(),
        session_id=session_id,
        rubric_json={},
        created_at=now,
        updated_at=now,
    )


def _get_summary(
    db: Session,
    session_id: uuid.UUID,
) -> InterviewRealtimeSummary | None:
    return (
        db.query(InterviewRealtimeSummary)
        .filter(InterviewRealtimeSummary.session_id == session_id)
        .one_or_none()
    )


def _validated_trusted_score(value: Any) -> dict[str, float] | None:
    if not isinstance(value, dict):
        return None
    meta = value.get("_meta")
    if not isinstance(meta, dict) or meta.get("source") not in {
        "server_deterministic",
        "server_evaluator",
    }:
        return None
    output: dict[str, float] = {}
    for dimension in RUBRIC_DIMENSIONS:
        raw = value.get(dimension)
        if raw is None or isinstance(raw, bool):
            return None
        try:
            score = float(raw)
        except (TypeError, ValueError):
            return None
        if not 0 <= score <= 5:
            return None
        output[dimension] = score
    return output


def _turn_recommendations(score: dict[str, float]) -> list[str]:
    weakest = sorted(POSITIVE_DIMENSIONS, key=score.get)[:2]
    output = [_improvement_for(dimension) for dimension in weakest]
    if score["risk"] >= 2.5:
        output.append("Replace absolute or unsupported claims with verifiable evidence.")
    return output


def _improvement_for(dimension: str) -> str:
    guidance = {
        "relevance": "Answer the exact question first, then connect the example to the target role.",
        "specificity": "Add concrete tools, scope, decisions, and outcomes that you can verify.",
        "evidence": "Ground the answer in a real project or profile example without inventing facts.",
        "structure": "Use a concise Situation-Task-Action-Result sequence.",
        "technical_depth": "Explain the technical choice, tradeoff, implementation, and result in more depth.",
        "communication_clarity": "Use shorter sentences and a clear beginning, middle, and conclusion.",
    }
    return guidance[dimension]


def _tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    return set(re.findall(r"[a-z0-9+#.-]+", value.lower()))


def _bounded(value: float) -> float:
    return round(max(0.0, min(5.0, value)), 2)
