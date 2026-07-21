"""Build minimal, ownership-scoped context for a realtime interview."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AnalysisJob, Application, CareerProfileItem
from app.services.interview_realtime.errors import RealtimeInterviewNotFound


_MAX_JD_REQUIREMENTS = 8
_MAX_SKILLS = 12
_MAX_EVIDENCE = 8
_MAX_PROFILE_ITEMS = 8


@dataclass(frozen=True)
class ContextSources:
    target_job: Application | None = None
    application: Application | None = None
    analysis_job: AnalysisJob | None = None


@dataclass(frozen=True)
class InterviewContext:
    target_job: dict[str, Any] | None = None
    application: dict[str, Any] | None = None
    analysis: dict[str, Any] | None = None
    profile_evidence: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def as_prompt_payload(self) -> dict[str, Any]:
        return {
            "target_job": self.target_job,
            "application": self.application,
            "analysis": self.analysis,
            "profile_evidence": self.profile_evidence,
            "limitations": self.limitations,
        }


def load_owned_context_sources(
    db: Session,
    user_id: uuid.UUID,
    *,
    target_job_id: uuid.UUID | None,
    application_id: uuid.UUID | None,
    analysis_job_id: uuid.UUID | None,
) -> ContextSources:
    """Load only explicitly linked resources and enforce non-leaking ownership."""
    target_job = _owned_application(db, user_id, target_job_id, "target job")
    application = _owned_application(db, user_id, application_id, "application")

    analysis_job: AnalysisJob | None = None
    if analysis_job_id is not None:
        analysis_job = _owned_analysis(db, user_id, analysis_job_id)
    else:
        for resource in (application, target_job):
            if resource is not None and resource.best_analysis_job_id is not None:
                analysis_job = _owned_analysis(
                    db, user_id, resource.best_analysis_job_id
                )
                break

    return ContextSources(
        target_job=target_job,
        application=application,
        analysis_job=analysis_job,
    )


def build_interview_context(
    db: Session,
    user_id: uuid.UUID,
    sources: ContextSources,
) -> InterviewContext:
    limitations: list[str] = []
    analysis = _analysis_context(sources.analysis_job)
    if analysis is None:
        limitations.append(
            "No completed owned analysis was available; do not assume skills or experience."
        )

    target_job = _application_context(sources.target_job)
    application = _application_context(sources.application)
    if target_job is None and application is None:
        limitations.append(
            "No target job or application was linked; use general interview questions."
        )

    relevance_terms = _relevance_terms(target_job, application, analysis)
    profile_evidence = _profile_context(db, user_id, relevance_terms)
    if not profile_evidence:
        limitations.append(
            "No clearly related profile evidence was included; ask the candidate for real examples."
        )

    return InterviewContext(
        target_job=target_job,
        application=application,
        analysis=analysis,
        profile_evidence=profile_evidence,
        limitations=limitations,
    )


def _owned_application(
    db: Session,
    user_id: uuid.UUID,
    resource_id: uuid.UUID | None,
    label: str,
) -> Application | None:
    if resource_id is None:
        return None
    resource = db.get(Application, resource_id)
    if resource is None or resource.user_id != user_id:
        raise RealtimeInterviewNotFound(f"{label} not found")
    return resource


def _owned_analysis(
    db: Session,
    user_id: uuid.UUID,
    job_id: uuid.UUID,
) -> AnalysisJob:
    job = db.get(AnalysisJob, job_id)
    if job is None or job.user_id != user_id:
        raise RealtimeInterviewNotFound("analysis job not found")
    return job


def _application_context(resource: Application | None) -> dict[str, Any] | None:
    if resource is None:
        return None
    return {
        "job_title": _trim(resource.job_title, 255),
        "company_name": _trim(resource.company_name, 255),
        "target_role": _trim(resource.target_role, 255),
        "job_requirements_summary": _summarize_job_description(resource.jd_text),
        "readiness_status": resource.status,
        "readiness_score": resource.last_readiness_score,
    }


def _analysis_context(job: AnalysisJob | None) -> dict[str, Any] | None:
    if job is None or job.status != "succeeded" or not isinstance(job.result_json, dict):
        return None

    envelope = job.result_json
    payload = envelope.get("result")
    result = payload if isinstance(payload, dict) else envelope

    fit_score = _first_number(
        envelope.get("overall_fit_score"),
        result.get("fit_score"),
        _dict(result.get("overall")).get("fit_score"),
        _dict(result.get("scores")).get("fit_score"),
    )
    matched = _skill_summaries(result.get("matched_skills"), missing=False)
    missing = _skill_summaries(result.get("missing_skills"), missing=True)

    score_breakdown: list[dict[str, Any]] = []
    raw_breakdown = result.get("score_breakdown")
    if isinstance(raw_breakdown, list):
        for item in raw_breakdown[:8]:
            if not isinstance(item, dict):
                continue
            score_breakdown.append(
                {
                    "key": _trim(item.get("key"), 80),
                    "label": _trim(item.get("label"), 120),
                    "score": _first_number(item.get("score")),
                    "explanation": _trim(item.get("explanation"), 320),
                }
            )
    elif isinstance(result.get("scores"), dict):
        for key, value in list(result["scores"].items())[:8]:
            number = _first_number(value)
            if number is not None:
                score_breakdown.append({"key": str(key)[:80], "score": number})

    evidence: list[dict[str, Any]] = []
    raw_evidence = result.get("evidence")
    if isinstance(raw_evidence, list):
        for item in raw_evidence:
            if len(evidence) >= _MAX_EVIDENCE:
                break
            if not isinstance(item, dict) or str(item.get("source") or "").lower() != "cv":
                continue
            evidence.append(
                {
                    "kind": _trim(item.get("kind"), 80),
                    "skill": _trim(item.get("normalized_skill"), 120),
                    "summary": _trim(item.get("text"), 320),
                }
            )

    readiness = _readiness_summary(fit_score, matched, missing)
    return {
        "fit_score": fit_score,
        "score_breakdown": score_breakdown,
        "matched_skills": matched,
        "missing_skills": missing,
        "cv_evidence_summaries": evidence,
        "readiness": readiness,
        "limitations": [
            _trim(value, 300)
            for value in _string_list(result.get("limitations"), limit=4)
        ],
    }


def _skill_summaries(raw: Any, *, missing: bool) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    if not isinstance(raw, list):
        return output
    for item in raw[:_MAX_SKILLS]:
        if isinstance(item, str):
            output.append({"skill": _trim(item, 120)})
            continue
        if not isinstance(item, dict):
            continue
        summary_key = "reason" if missing else "notes"
        output.append(
            {
                "skill": _trim(item.get("skill") or item.get("name"), 120),
                "requirement": _trim(item.get("jd_requirement"), 300),
                "summary": _trim(item.get(summary_key), 300),
            }
        )
    return [item for item in output if item.get("skill")]


def _profile_context(
    db: Session,
    user_id: uuid.UUID,
    relevance_terms: set[str],
) -> list[dict[str, Any]]:
    items = (
        db.query(CareerProfileItem)
        .filter(CareerProfileItem.user_id == user_id)
        .order_by(CareerProfileItem.updated_at.desc())
        .limit(50)
        .all()
    )
    output: list[dict[str, Any]] = []
    for item in items:
        skills = [
            _trim(skill, 100)
            for skill in (item.skills_json or [])
            if isinstance(skill, str) and _trim(skill, 100)
        ][:10]
        searchable = " ".join(
            value
            for value in [item.title or "", item.description or "", " ".join(skills)]
            if value
        ).lower()
        if relevance_terms and not any(term in searchable for term in relevance_terms):
            continue
        output.append(
            {
                "item_type": item.item_type,
                "title": _trim(item.title, 200),
                "description_summary": _trim(item.description, 360),
                "skills": skills,
            }
        )
        if len(output) >= _MAX_PROFILE_ITEMS:
            break
    return output


def _relevance_terms(*sections: dict[str, Any] | None) -> set[str]:
    text_parts: list[str] = []
    for section in sections:
        if not section:
            continue
        text_parts.extend(_flatten_short_strings(section))
    return {
        token
        for token in re.findall(r"[a-z0-9+#.-]{3,}", " ".join(text_parts).lower())
        if token not in {"with", "from", "this", "that", "have", "skill", "score"}
    }


def _flatten_short_strings(value: Any) -> list[str]:
    output: list[str] = []
    if isinstance(value, str):
        output.append(value[:300])
    elif isinstance(value, dict):
        for nested in value.values():
            output.extend(_flatten_short_strings(nested))
    elif isinstance(value, list):
        for nested in value[:20]:
            output.extend(_flatten_short_strings(nested))
    return output


def _summarize_job_description(value: str | None) -> list[str]:
    text = _trim(value, 12000)
    if not text:
        return []
    fragments = [
        _trim(fragment, 360)
        for fragment in re.split(r"(?:\r?\n|(?<=[.!?])\s+)", text)
        if _trim(fragment, 360)
    ]
    keywords = (
        "require",
        "responsib",
        "experience",
        "skill",
        "qualification",
        "must",
        "preferred",
        "proficien",
    )
    preferred = [item for item in fragments if any(key in item.lower() for key in keywords)]
    selected = preferred or fragments
    return selected[:_MAX_JD_REQUIREMENTS]


def _readiness_summary(
    fit_score: float | None,
    matched: list[dict[str, Any]],
    missing: list[dict[str, Any]],
) -> dict[str, Any]:
    if fit_score is None:
        level = "unknown"
    elif fit_score >= 75:
        level = "ready"
    elif fit_score >= 55:
        level = "almost_ready"
    else:
        level = "needs_work"
    return {
        "level": level,
        "matched_skills_count": len(matched),
        "missing_skills_count": len(missing),
    }


def _string_list(value: Any, *, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value[:limit] if isinstance(item, str)]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _first_number(*values: Any) -> float | None:
    for value in values:
        if value is None or isinstance(value, bool):
            continue
        try:
            return round(float(value), 2)
        except (TypeError, ValueError):
            continue
    return None


def _trim(value: Any, limit: int) -> str | None:
    if value is None:
        return None
    normalized = re.sub(r"\s+", " ", str(value)).strip()
    if not normalized:
        return None
    return normalized[:limit]
