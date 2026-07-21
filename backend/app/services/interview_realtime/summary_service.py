"""Deterministic Phase 8 rubric aggregation and persistence foundation."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    InterviewRealtimeSession,
    InterviewRealtimeSummary,
    InterviewRealtimeTurn,
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


def generate_deterministic_summary_if_ready(
    db: Session,
    session: InterviewRealtimeSession,
) -> InterviewRealtimeSummary | None:
    """Persist a summary only when every completed turn has trusted score_json."""
    turns = (
        db.query(InterviewRealtimeTurn)
        .filter(InterviewRealtimeTurn.session_id == session.id)
        .order_by(InterviewRealtimeTurn.turn_index.asc())
        .all()
    )
    if not turns:
        return None

    scores: list[dict[str, float]] = []
    for turn in turns:
        score = _validated_score(turn.score_json)
        if score is None:
            return None
        scores.append(score)

    rubric = {
        dimension: round(
            sum(score[dimension] for score in scores) / len(scores), 2
        )
        for dimension in RUBRIC_DIMENSIONS
    }
    positive_average = sum(rubric[dimension] for dimension in POSITIVE_DIMENSIONS) / len(
        POSITIVE_DIMENSIONS
    )
    risk_component = 5 - rubric["risk"]
    overall_score = round(((positive_average * 0.85) + (risk_component * 0.15)) * 20)
    overall_score = max(0, min(100, overall_score))

    strengths = [
        f"Consistent {_DIMENSION_LABELS[dimension]}."
        for dimension in POSITIVE_DIMENSIONS
        if rubric[dimension] >= 3.5
    ]
    weaknesses = [
        f"Needs more {_DIMENSION_LABELS[dimension]}."
        for dimension in POSITIVE_DIMENSIONS
        if rubric[dimension] < 2.5
    ]
    if rubric["risk"] >= 2.5:
        weaknesses.append(
            "Some answers carry elevated risk from gaps or unsupported claims."
        )

    weakest_dimensions = sorted(
        POSITIVE_DIMENSIONS,
        key=lambda dimension: rubric[dimension],
    )[:2]
    improvements = [
        _improvement_for(dimension) for dimension in weakest_dimensions
    ]
    if rubric["risk"] >= 2.5:
        improvements.append(
            "Separate verified experience from skills you are still learning, and avoid unsupported claims."
        )

    next_questions = [
        f"Practice one job-relevant answer focused on {_DIMENSION_LABELS[dimension]}."
        for dimension in weakest_dimensions
    ]
    learning_tasks = [
        {
            "task_type": "interview_prep",
            "priority": "high" if rubric[dimension] < 2 else "medium",
            "title": f"Improve {_DIMENSION_LABELS[dimension]}",
            "description": _improvement_for(dimension),
        }
        for dimension in weakest_dimensions
    ]
    limitations = [
        "This deterministic summary uses only stored turn rubric scores; it does not independently verify transcript claims.",
        "It does not evaluate emotion, facial expression, personality, truthfulness, or hiring probability.",
        "Practice feedback does not guarantee interview or hiring outcomes.",
    ]

    summary = (
        db.query(InterviewRealtimeSummary)
        .filter(InterviewRealtimeSummary.session_id == session.id)
        .one_or_none()
    )
    now = datetime.utcnow()
    if summary is None:
        summary = InterviewRealtimeSummary(
            id=uuid.uuid4(),
            session_id=session.id,
            created_at=now,
            updated_at=now,
        )
        db.add(summary)

    summary.overall_score = overall_score
    summary.rubric_json = rubric
    summary.strengths_json = strengths
    summary.weaknesses_json = weaknesses
    summary.suggested_improvements_json = improvements
    summary.next_questions_json = next_questions
    summary.learning_tasks_json = learning_tasks
    summary.limitations_json = limitations
    summary.updated_at = now
    return summary


def _validated_score(value: Any) -> dict[str, float] | None:
    if not isinstance(value, dict):
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
