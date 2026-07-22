"""Server-side deterministic Phase 8 transcript evaluation and summaries."""

from __future__ import annotations

import re
import unicodedata
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
EVALUATOR_VERSION = "deterministic_transcript_v2_unicode"
TRANSCRIPT_PROVENANCE = "client_reported_validated"
SUMMARY_DISCLAIMER = (
    "Phản hồi phỏng vấn AI chỉ phục vụ luyện tập và không dự đoán kết quả tuyển dụng."
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
    "relevance": "mức độ liên quan đến công việc",
    "specificity": "chi tiết cụ thể",
    "evidence": "bằng chứng thực tế",
    "structure": "cấu trúc câu trả lời",
    "technical_depth": "chiều sâu kỹ thuật",
    "communication_clarity": "độ rõ ràng khi giao tiếp",
    "risk": "rủi ro từ tuyên bố thiếu căn cứ",
}
_TECHNICAL_TERMS = {
    ".net",
    "api",
    "architecture",
    "backend",
    "cache",
    "c#",
    "c++",
    "ci/cd",
    "database",
    "deploy",
    "design",
    "fastapi",
    "framework",
    "latency",
    "migration",
    "next.js",
    "performance",
    "postgresql",
    "python",
    "query",
    "react.js",
    "render",
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
    "xây",
    "thiết kế",
    "triển khai",
    "cải thiện",
    "dẫn dắt",
    "tối ưu",
    "giải quyết",
    "kiểm thử",
    "chịu trách nhiệm",
    "phát triển",
}
_RESULT_TERMS = {
    "delivered",
    "improved",
    "increased",
    "reduced",
    "result",
    "saved",
    "success",
    "kết quả",
    "thành công",
    "giảm",
    "tăng",
    "tiết kiệm",
}
_STRUCTURE_TERMS = {
    "situation", "task", "action", "result", "first", "then", "finally",
    "tình huống", "nhiệm vụ", "hành động", "kết quả", "đầu tiên", "sau đó", "cuối cùng",
}
_UNSUPPORTED_CLAIM_TERMS = {
    "always",
    "best",
    "expert",
    "guarantee",
    "never fail",
    "perfect",
    "100%",
    "luôn luôn",
    "tốt nhất",
    "chuyên gia",
    "đảm bảo",
    "không bao giờ thất bại",
    "hoàn hảo",
}

# Python's ``re`` engine treats ``\w`` as Unicode by default. The pattern keeps
# Vietnamese letters intact and preserves the technical spellings that carry
# meaning in interview answers (for example React.js, C++, .NET, and CI/CD).
_TOKEN_PATTERN = re.compile(
    r"(?:\.[^\W_][\w]*|[^\W_][\w]*)(?:[./-][^\W_][\w]*)*(?:\+\+|#|%)?",
    flags=re.UNICODE,
)


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
            "Bản ghi lời thoại do trình duyệt báo cáo và không được nhà cung cấp xác minh bằng mật mã.",
            SUMMARY_DISCLAIMER,
        ],
    }
    return score


def _score_turn(question_text: str | None, answer_text: str | None) -> dict[str, float]:
    question_sequence = _token_sequence(question_text)
    answer_sequence = _token_sequence(answer_text)
    question_tokens = set(question_sequence)
    answer_tokens = set(answer_sequence)
    word_count = len(answer_sequence)
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
    action_count = _matching_term_count(answer_sequence, _ACTION_TERMS)
    result_count = _matching_term_count(answer_sequence, _RESULT_TERMS)
    quantified_result_count = _quantified_result_count(
        answer_sequence,
        has_result_term=result_count > 0,
    )
    structure_count = _matching_term_count(answer_sequence, _STRUCTURE_TERMS)
    technical_count = _matching_term_count(answer_sequence, _TECHNICAL_TERMS)
    first_person = bool(
        _matching_term_count(
            answer_sequence,
            {"i", "my", "we", "our", "tôi", "mình", "chúng tôi", "chúng ta"},
        )
    )
    unsupported_count = _matching_term_count(
        answer_sequence,
        _UNSUPPORTED_CLAIM_TERMS,
    )

    relevance = _bounded(1.0 + (overlap * 2.5) + (length_factor * 1.5))
    specificity = _bounded(0.8 + (length_factor * 2.0) + min(digit_count, 2) * 0.5 + min(technical_count, 3) * 0.25)
    evidence = _bounded(0.5 + (1.0 if first_person else 0.0) + min(action_count, 2) * 0.8 + min(result_count + quantified_result_count, 2) * 0.7)
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
        f"Thể hiện ổn định về {_DIMENSION_LABELS[dimension]}."
        for dimension in POSITIVE_DIMENSIONS
        if averages[dimension] >= 3.5
    ]
    weaknesses = [
        f"Cần cải thiện thêm về {_DIMENSION_LABELS[dimension]}."
        for dimension in POSITIVE_DIMENSIONS
        if averages[dimension] < 2.5
    ]
    if averages["risk"] >= 2.5:
        weaknesses.append("Một số câu trả lời có dấu hiệu chứa tuyên bố thiếu căn cứ.")

    weakest_dimensions = sorted(POSITIVE_DIMENSIONS, key=averages.get)[:2]
    improvements = [_improvement_for(dimension) for dimension in weakest_dimensions]
    if averages["risk"] >= 2.5:
        improvements.append(
            "Phân biệt rõ kinh nghiệm đã được kiểm chứng với kỹ năng đang học và tránh khẳng định tuyệt đối."
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
            "title": f"Cải thiện {_DIMENSION_LABELS[dimension]}",
            "description": _improvement_for(dimension),
            "source": "realtime_interview_summary",
            "rubric_version": RUBRIC_VERSION,
        }
        for dimension in weakest_dimensions
    ]
    limitations = [
        "Bản ghi lời thoại do trình duyệt báo cáo và không được nhà cung cấp xác minh bằng mật mã.",
        "Rubric luyện tập xác định này dùng heuristic văn bản có giới hạn và vẫn cần đánh giá chất lượng độc lập.",
        "Hệ thống không đánh giá cảm xúc, biểu cảm khuôn mặt, tính cách, độ trung thực, thuộc tính được bảo vệ hoặc xác suất tuyển dụng.",
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
        f"Luyện thêm một câu trả lời liên quan công việc, tập trung vào {_DIMENSION_LABELS[dimension]}."
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
        "Việc tạo đánh giá đã thất bại an toàn; các lượt lời đã lưu được giữ lại để thử lại.",
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
        output.append("Thay các khẳng định tuyệt đối hoặc thiếu căn cứ bằng bằng chứng có thể kiểm chứng.")
    return output


def _improvement_for(dimension: str) -> str:
    guidance = {
        "relevance": "Trả lời trực tiếp câu hỏi trước, sau đó liên hệ ví dụ với vị trí mục tiêu.",
        "specificity": "Bổ sung công cụ, phạm vi, quyết định và kết quả cụ thể có thể kiểm chứng.",
        "evidence": "Dựa câu trả lời trên dự án hoặc ví dụ hồ sơ có thật, không bịa dữ kiện.",
        "structure": "Dùng trình tự ngắn gọn Tình huống-Nhiệm vụ-Hành động-Kết quả.",
        "technical_depth": "Giải thích sâu hơn lựa chọn kỹ thuật, đánh đổi, cách triển khai và kết quả.",
        "communication_clarity": "Dùng câu ngắn hơn với phần mở đầu, nội dung và kết luận rõ ràng.",
    }
    return guidance[dimension]


def _tokens(value: str | None) -> set[str]:
    return set(_token_sequence(value))


def _token_sequence(value: str | None) -> tuple[str, ...]:
    """Return stable NFC/case-folded Unicode tokens in source order."""
    if not value:
        return ()
    normalized = unicodedata.normalize("NFC", value).casefold()
    return tuple(
        token
        for match in _TOKEN_PATTERN.finditer(normalized)
        if (token := match.group(0))
    )


def _matching_term_count(
    tokens: tuple[str, ...],
    terms: set[str],
) -> int:
    """Count distinct single- or multi-token rubric terms without substring matches."""
    if not tokens:
        return 0
    count = 0
    for term in terms:
        phrase = _token_sequence(term)
        if not phrase or len(phrase) > len(tokens):
            continue
        if any(
            tokens[index : index + len(phrase)] == phrase
            for index in range(len(tokens) - len(phrase) + 1)
        ):
            count += 1
    return count


def _quantified_result_count(
    tokens: tuple[str, ...],
    *,
    has_result_term: bool,
) -> int:
    """Count numeric evidence only when it looks like an outcome, not fake JSON."""
    numeric = [token for token in tokens if any(char.isdigit() for char in token)]
    if has_result_term:
        return len(numeric)
    return sum(token.endswith("%") for token in numeric)


def _bounded(value: float) -> float:
    return round(max(0.0, min(5.0, value)), 2)
