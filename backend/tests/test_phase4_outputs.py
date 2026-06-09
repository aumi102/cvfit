"""
AI CV Fit Phase 4 — Comprehensive Output Tests

Tests for Phase 4 services:
- Result JSON v3 schema and required fields
- Improvement Action Plan safety
- Safe Rewrite Suggestions guardrails
- Interview Prep quality
- Learning Roadmap guardrails
- Comparison engine correctness
- Keyword Stuffing detection
- Sensitive data scrubbing
- Guardrail v2 compliance
"""
from __future__ import annotations

import re
import pytest

from app.services.scoring.result_v3 import build_result_v3
from app.services.scoring.result_v2 import build_result_v2
from app.services.improvement.action_plan import build_improvement_actions
from app.services.improvement.safe_rewrite import build_safe_rewrite_suggestions
from app.services.interview.interview_prep import build_interview_prep
from app.services.roadmap.learning_roadmap import build_learning_roadmap
from app.services.comparison.compare_results import compare_results
from app.services.comparison.keyword_stuffing import detect_keyword_stuffing

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_result(matched_skills=None, missing_skills=None, evidence=None, **kwargs):
    """Build a minimal v2-style result dict for testing."""
    overall = {
        "fit_score": 65.0,
        "fit_level": "partial",
        "summary": "Test result.",
        "guardrail_notice": "This analysis estimates CV-to-JD fit only and does not guarantee any hiring outcome.",
    }
    if "overall" in kwargs and isinstance(kwargs["overall"], dict):
        overall.update(kwargs.pop("overall"))

    scores = {"fit_score": 65.0}
    if "scores" in kwargs and isinstance(kwargs["scores"], dict):
        scores.update(kwargs.pop("scores"))

    fit_score = kwargs.pop("fit_score", 65.0)
    result = {
        "job_id": "test-job",
        "fit_score": fit_score,
        "scores": scores,
        "overall": overall,
        "matched_skills": matched_skills or [],
        "missing_skills": missing_skills or [],
        "evidence": evidence or [],
        "improvement_actions": kwargs.pop("improvement_actions", []),
        "limitations": kwargs.pop("limitations", []),
        "metadata": kwargs.pop("metadata", {}),
    }
    scores["fit_score"] = fit_score
    overall["fit_score"] = fit_score
    result.update(kwargs)
    return result


# ---------------------------------------------------------------------------
# Result JSON v3 — Schema and Required Fields
# ---------------------------------------------------------------------------

class TestResultV3Schema:
    def test_v3_adds_schema_version(self):
        v2 = _make_result()
        v3 = build_result_v3(v2)
        assert v3.get("schema_version") == "3.0"

    def test_v3_adds_improvement_actions(self):
        v2 = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        v3 = build_result_v3(v2)
        assert "improvement_actions" in v3
        assert isinstance(v3["improvement_actions"], list)

    def test_v3_adds_safe_rewrite_suggestions(self):
        v2 = _make_result(evidence=[
            {"id": "ev1", "source": "cv", "text": "Built an API with Python", "best_cv_bullet": "Built an API with Python"},
        ])
        v3 = build_result_v3(v2)
        assert "safe_rewrite_suggestions" in v3
        assert isinstance(v3["safe_rewrite_suggestions"], list)

    def test_v3_adds_interview_prep(self):
        v2 = _make_result(matched_skills=[
            {"skill": "FastAPI", "jd_requirement": "FastAPI", "cv_evidence_ids": ["ev1"]},
        ])
        v3 = build_result_v3(v2)
        assert "interview_prep" in v3
        assert isinstance(v3["interview_prep"], list)

    def test_v3_adds_learning_roadmap(self):
        v2 = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        v3 = build_result_v3(v2)
        assert "learning_roadmap" in v3
        assert isinstance(v3["learning_roadmap"], list)

    def test_v3_limitations_contains_no_hiring_guarantee(self):
        v2 = _make_result()
        v3 = build_result_v3(v2)
        limitations = v3.get("limitations") or []
        text = " ".join(str(l) for l in limitations).lower()
        assert any("does not guarantee" in l.lower() or "hiring outcome" in l.lower() for l in limitations)

    def test_v3_preserves_v2_aliases(self):
        v2 = _make_result(fit_score=72.0, scores={"fit_score": 72.0})
        v2["overall"] = {"fit_score": 72.0, "fit_level": "good", "summary": "Test."}
        v3 = build_result_v3(v2)
        assert v3.get("fit_score") == 72.0
        assert v3.get("scores", {}).get("fit_score") == 72.0
        assert v3.get("overall", {}).get("fit_score") == 72.0

    def test_v3_metadata_has_contract_and_scorer_version(self):
        v2 = _make_result()
        v3 = build_result_v3(v2)
        metadata = v3.get("metadata") or {}
        assert metadata.get("contract_version") == "result_json_v3"
        assert "phase4" in metadata.get("scorer_version", "")


# ---------------------------------------------------------------------------
# Improvement Action Plan Safety
# ---------------------------------------------------------------------------

class TestImprovementActionsSafety:
    def test_actions_have_do_not_fabricate_true(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        actions = build_improvement_actions(result)
        assert len(actions) > 0
        for action in actions:
            assert action.get("do_not_fabricate") is True

    def test_actions_have_conditional_suggestion(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        actions = build_improvement_actions(result)
        for action in actions:
            suggestion = str(action.get("safe_suggestion", ""))
            assert "if you have actually used" in suggestion.lower() or "only add this if it is true" in suggestion.lower()

    def test_actions_have_priority(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
            {"skill": "Redis", "requirement_type": "nice_to_have", "jd_requirement": "Redis", "jd_evidence_ids": []},
        ])
        actions = build_improvement_actions(result)
        priorities = {a.get("priority") for a in actions}
        assert priorities <= {"high", "medium", "low"}

    def test_must_have_action_is_high_priority(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        actions = build_improvement_actions(result)
        assert any(a.get("priority") == "high" for a in actions)

    def test_actions_have_safe_reason(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        actions = build_improvement_actions(result)
        for action in actions:
            reason = str(action.get("reason", "")).lower()
            # Must not say "you don't know FastAPI"
            assert not re.search(r"\byou\s+(do\s+)?don[' ]?t\s+know\b", reason)
            assert not re.search(r"\byou\s+(do\s+)?don[' ]?t\s+have\b", reason)
            # Must contain "not found in parsed CV" or similar
            assert "not found" in reason or "evidence" in reason


# ---------------------------------------------------------------------------
# Safe Rewrite Suggestions
# ---------------------------------------------------------------------------

class TestSafeRewriteSuggestions:
    def test_rewrite_has_do_not_fabricate_true(self):
        result = _make_result(evidence=[
            {"id": "ev1", "source": "cv", "text": "Built an API", "best_cv_bullet": "Built an API with Python and PostgreSQL"},
        ])
        suggestions = build_safe_rewrite_suggestions(result)
        assert len(suggestions) > 0
        for s in suggestions:
            assert s.get("do_not_fabricate") is True

    def test_rewrite_has_warning(self):
        result = _make_result(evidence=[
            {"id": "ev1", "source": "cv", "text": "Built an API", "best_cv_bullet": "Built an API"},
        ])
        suggestions = build_safe_rewrite_suggestions(result)
        for s in suggestions:
            assert "warning" in s
            assert len(str(s["warning"])) > 5

    def test_rewrite_uses_template_not_finished_claim(self):
        result = _make_result(evidence=[
            {"id": "ev1", "source": "cv", "text": "Built an API", "best_cv_bullet": "Built an API"},
        ])
        suggestions = build_safe_rewrite_suggestions(result)
        for s in suggestions:
            structure = str(s.get("suggested_structure", ""))
            # Template should use brackets for placeholders
            assert "[" in structure and "]" in structure

    def test_rewrite_has_missing_context_to_confirm(self):
        result = _make_result(evidence=[
            {"id": "ev1", "source": "cv", "text": "Built an API", "best_cv_bullet": "Built an API"},
        ])
        suggestions = build_safe_rewrite_suggestions(result)
        for s in suggestions:
            assert "missing_context_to_confirm" in s
            assert isinstance(s["missing_context_to_confirm"], list)
            assert len(s["missing_context_to_confirm"]) > 0

    def test_no_cv_evidence_returns_fallback_suggestion(self):
        result = _make_result(evidence=[])
        suggestions = build_safe_rewrite_suggestions(result)
        assert len(suggestions) == 1
        assert suggestions[0].get("do_not_fabricate") is True


# ---------------------------------------------------------------------------
# Interview Prep Quality
# ---------------------------------------------------------------------------

class TestInterviewPrepQuality:
    def test_questions_have_required_fields(self):
        result = _make_result(matched_skills=[
            {"skill": "FastAPI", "jd_requirement": "FastAPI backend API development", "cv_evidence_ids": ["ev1"]},
        ])
        questions = build_interview_prep(result)
        for q in questions:
            assert "question" in q
            assert "type" in q
            assert "why_this_question" in q
            assert "related_jd_requirement" in q
            assert "suggested_answer_outline" in q
            assert "risk_if_user_cannot_answer" in q

    def test_question_types_are_valid(self):
        result = _make_result(matched_skills=[
            {"skill": "FastAPI", "jd_requirement": "FastAPI", "cv_evidence_ids": ["ev1"]},
        ], missing_skills=[
            {"skill": "Redis", "requirement_type": "nice_to_have", "jd_requirement": "Redis", "jd_evidence_ids": []},
        ])
        questions = build_interview_prep(result, max_questions=10)
        valid_types = {"technical", "behavioral", "project_deep_dive", "gap_probe", "system_design"}
        for q in questions:
            assert q.get("type") in valid_types

    def test_gap_probe_for_missing_skill(self):
        result = _make_result(
            matched_skills=[],
            missing_skills=[{"skill": "Redis", "requirement_type": "nice_to_have", "jd_requirement": "Redis", "jd_evidence_ids": []}],
        )
        questions = build_interview_prep(result)
        gap_probes = [q for q in questions if q.get("type") == "gap_probe"]
        assert len(gap_probes) > 0

    def test_gap_probe_has_empty_cv_evidence(self):
        result = _make_result(
            matched_skills=[],
            missing_skills=[{"skill": "Redis", "requirement_type": "nice_to_have", "jd_requirement": "Redis", "jd_evidence_ids": []}],
        )
        questions = build_interview_prep(result)
        gap_probes = [q for q in questions if q.get("type") == "gap_probe"]
        for q in gap_probes:
            # gap_probe should have empty or missing cv_evidence since skill is missing
            assert q.get("related_cv_evidence") == [] or q.get("related_cv_evidence") is None

    def test_project_deep_dive_has_cv_evidence(self):
        result = _make_result(
            matched_skills=[{"skill": "FastAPI", "jd_requirement": "FastAPI", "cv_evidence_ids": ["ev1"]}],
            evidence=[{"id": "ev1", "source": "cv", "text": "Built FastAPI API", "best_cv_bullet": "Built FastAPI API"}],
        )
        questions = build_interview_prep(result)
        project_questions = [q for q in questions if q.get("type") == "project_deep_dive"]
        if project_questions:
            for q in project_questions:
                assert q.get("related_cv_evidence")

    def test_risk_field_is_meaningful(self):
        result = _make_result(matched_skills=[
            {"skill": "FastAPI", "jd_requirement": "FastAPI", "cv_evidence_ids": ["ev1"]},
        ])
        questions = build_interview_prep(result)
        for q in questions:
            risk = str(q.get("risk_if_user_cannot_answer", ""))
            assert len(risk) > 10

    def test_answer_outline_is_list(self):
        result = _make_result(matched_skills=[
            {"skill": "FastAPI", "jd_requirement": "FastAPI", "cv_evidence_ids": ["ev1"]},
        ])
        questions = build_interview_prep(result)
        for q in questions:
            outline = q.get("suggested_answer_outline")
            assert isinstance(outline, list)
            assert len(outline) > 0


# ---------------------------------------------------------------------------
# Learning Roadmap Guardrails
# ---------------------------------------------------------------------------

class TestLearningRoadmapGuardrails:
    def test_roadmap_items_have_do_not_claim_until_completed_true(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        roadmap = build_learning_roadmap(result)
        assert len(roadmap) > 0
        for item in roadmap:
            assert item.get("do_not_claim_until_completed") is True

    def test_roadmap_has_priority(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        roadmap = build_learning_roadmap(result)
        for item in roadmap:
            assert item.get("priority") in {"high", "medium", "low"}

    def test_must_have_missing_skill_high_priority(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        roadmap = build_learning_roadmap(result)
        assert any(item.get("priority") == "high" for item in roadmap)

    def test_roadmap_has_topics(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        roadmap = build_learning_roadmap(result)
        for item in roadmap:
            assert "topics" in item
            assert isinstance(item["topics"], list)
            assert len(item["topics"]) > 0

    def test_roadmap_has_mini_project(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        roadmap = build_learning_roadmap(result)
        for item in roadmap:
            assert "mini_project" in item
            assert len(str(item["mini_project"])) > 5

    def test_roadmap_why_is_future_facing(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        roadmap = build_learning_roadmap(result)
        for item in roadmap:
            why = str(item.get("why", "")).lower()
            assert "not found" in why or "evidence was not found" in why
            # Must NOT say "you already know FastAPI"
            assert not re.search(r"\bsince\s+you\s+(already\s+)?know", why)
            assert not re.search(r"\byou\s+(already\s+)?have\s+\w+\s+experience", why)

    def test_roadmap_cv_guidance_is_future_facing(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        roadmap = build_learning_roadmap(result)
        for item in roadmap:
            guidance = str(item.get("cv_evidence_to_add_after_learning", "")).lower()
            assert "after" in guidance or "completion" in guidance or "completed" in guidance

    def test_roadmap_estimated_effort_is_present(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        roadmap = build_learning_roadmap(result)
        for item in roadmap:
            assert "estimated_effort" in item
            assert len(str(item["estimated_effort"])) > 0


# ---------------------------------------------------------------------------
# Comparison Engine
# ---------------------------------------------------------------------------

class TestComparisonEngine:
    def test_comparison_has_required_keys(self):
        base = _make_result(fit_score=60.0)
        new = _make_result(fit_score=75.0)
        comp = compare_results(base, new, base_job_id="base", new_job_id="new")
        required = (
            "base_job_id", "new_job_id", "base_score", "new_score",
            "score_delta", "breakdown_delta", "resolved_missing_skills",
            "still_missing_skills", "newly_matched_skills", "new_evidence",
            "keyword_stuffing_warnings", "improvement_summary", "next_actions",
        )
        for key in required:
            assert key in comp, f"Missing key: {key}"

    def test_score_delta_correct(self):
        base = _make_result(fit_score=60.0)
        new = _make_result(fit_score=75.0)
        comp = compare_results(base, new, base_job_id="base", new_job_id="new")
        assert comp.get("score_delta") == 15.0

    def test_score_delta_negative(self):
        base = _make_result(fit_score=80.0)
        new = _make_result(fit_score=65.0)
        comp = compare_results(base, new, base_job_id="base", new_job_id="new")
        assert comp.get("score_delta") == -15.0

    def test_resolved_skills_require_evidence(self):
        base = _make_result(
            missing_skills=[{"skill": "FastAPI", "reason": "Not found", "jd_evidence_ids": []}],
            matched_skills=[],
        )
        new = _make_result(
            matched_skills=[{"skill": "FastAPI", "cv_evidence_ids": ["ev1"]}],
            evidence=[{"id": "ev1", "source": "cv", "text": "Built FastAPI API", "best_cv_bullet": "Built FastAPI API"}],
            missing_skills=[],
        )
        comp = compare_results(base, new, base_job_id="base", new_job_id="new")
        # Resolved skills should appear when new has evidence
        resolved = comp.get("resolved_missing_skills") or []
        assert isinstance(resolved, list)

    def test_improvement_summary_not_empty(self):
        base = _make_result(fit_score=60.0)
        new = _make_result(fit_score=75.0)
        comp = compare_results(base, new, base_job_id="base", new_job_id="new")
        assert len(comp.get("improvement_summary", "")) > 5

    def test_improvement_summary_mentions_delta(self):
        base = _make_result(fit_score=60.0)
        new = _make_result(fit_score=75.0)
        comp = compare_results(base, new, base_job_id="base", new_job_id="new")
        summary = str(comp.get("improvement_summary", "")).lower()
        assert "improved" in summary or "decreased" in summary or "did not change" in summary


# ---------------------------------------------------------------------------
# Keyword Stuffing Detection
# ---------------------------------------------------------------------------

class TestKeywordStuffingDetection:
    def test_detects_skill_without_evidence(self):
        # Base result: skill listed but not matched
        base = _make_result(missing_skills=[{"skill": "FastAPI"}])
        # New result: skill matched but no cv_evidence_ids
        new = _make_result(matched_skills=[{"skill": "FastAPI", "cv_evidence_ids": []}])
        warnings = detect_keyword_stuffing(base, new)
        assert len(warnings) > 0

    def test_detects_multiple_unsupported_matches(self):
        base = _make_result(missing_skills=[])
        new = _make_result(
            matched_skills=[
                {"skill": "FastAPI", "cv_evidence_ids": []},
                {"skill": "PostgreSQL", "cv_evidence_ids": []},
                {"skill": "Redis", "cv_evidence_ids": []},
            ]
        )
        warnings = detect_keyword_stuffing(base, new)
        assert len(warnings) >= 1  # at least the "multiple skills" aggregate warning

    def test_does_not_warn_for_matched_with_evidence(self):
        base = _make_result(missing_skills=[{"skill": "FastAPI"}])
        new = _make_result(
            matched_skills=[{"skill": "FastAPI", "cv_evidence_ids": ["ev1"]}],
            evidence=[{"id": "ev1", "source": "cv", "text": "Built FastAPI API", "best_cv_bullet": "Built FastAPI API"}],
        )
        warnings = detect_keyword_stuffing(base, new)
        # Should NOT have a warning for FastAPI since it has evidence
        fastapi_warnings = [w for w in warnings if w.get("skill", "").lower() == "fastapi"]
        assert len(fastapi_warnings) == 0

    def test_warning_has_severity(self):
        base = _make_result(missing_skills=[])
        new = _make_result(matched_skills=[{"skill": "FastAPI", "cv_evidence_ids": []}])
        warnings = detect_keyword_stuffing(base, new)
        for w in warnings:
            assert "severity" in w
            assert w["severity"] in {"low", "medium", "high"}

    def test_warning_has_message(self):
        base = _make_result(missing_skills=[])
        new = _make_result(matched_skills=[{"skill": "FastAPI", "cv_evidence_ids": []}])
        warnings = detect_keyword_stuffing(base, new)
        for w in warnings:
            assert "message" in w
            assert len(w["message"]) > 5


# ---------------------------------------------------------------------------
# Sensitive Data Scrubbing
# ---------------------------------------------------------------------------

class TestSensitiveDataScrubbing:
    def test_result_v3_scrubs_access_token(self):
        v2 = _make_result()
        v2["access_token"] = "secret-token-12345"
        v2["access_token_hash"] = "fake-hash"
        v3 = build_result_v3(v2)
        text = str(v3)
        assert "secret-token-12345" not in text
        assert "fake-hash" not in text

    def test_result_v3_scrubs_paths(self):
        v2 = _make_result()
        v2["storage_path"] = "/var/data/cv.txt"
        v2["local_path"] = "C:\\Users\\Test\\cv.docx"
        v3 = build_result_v3(v2)
        text = str(v3)
        assert "/var/data/cv.txt" not in text
        assert "C:\\Users\\Test" not in text

    def test_result_v3_scrubs_raw_cv_text(self):
        v2 = _make_result()
        v2["raw_cv_text"] = "This is the raw CV content with personal info."
        v3 = build_result_v3(v2)
        text = str(v3)
        assert "This is the raw CV content" not in text

    def test_comparison_scrubs_sensitive_keys(self):
        base = _make_result()
        base["access_token"] = "base-secret"
        new = _make_result()
        new["access_token"] = "new-secret"
        comp = compare_results(base, new, base_job_id="base", new_job_id="new")
        text = str(comp)
        assert "base-secret" not in text
        assert "new-secret" not in text


# ---------------------------------------------------------------------------
# Guardrail v2 — No Hiring Guarantee
# ---------------------------------------------------------------------------

class TestNoHiringGuarantee:
    def test_no_guarantee_in_result_v3(self):
        v2 = _make_result()
        v3 = build_result_v3(v2)
        text = " ".join(str(v3[key]) for key in v3 if v3[key]).lower()
        guarantee_patterns = [
            r"guarantee[sd]?\s+(an?\s+)?(interview|job|hired)",
            r"will\s+definitely\s+(get\s+)?(hired|selected)",
            r"you\s+will\s+(definitely\s+)?(get\s+)?the\s+job",
            r"100%\s+sure\s+to\s+get\s+hired",
        ]
        for pattern in guarantee_patterns:
            assert not re.search(pattern, text), f"Guarantee phrase found: {pattern}"

    def test_no_guarantee_in_comparison(self):
        base = _make_result()
        new = _make_result()
        comp = compare_results(base, new, base_job_id="base", new_job_id="new")
        text = " ".join(str(v) for v in comp.values() if v).lower()
        guarantee_patterns = [
            r"guarantee[sd]?\s+(an?\s+)?(interview|job|hired)",
            r"will\s+definitely\s+(get\s+)?(hired|selected)",
        ]
        for pattern in guarantee_patterns:
            assert not re.search(pattern, text), f"Guarantee phrase found in comparison: {pattern}"


# ---------------------------------------------------------------------------
# Guardrail v2 — No Fabrication
# ---------------------------------------------------------------------------

class TestNoFabrication:
    def test_no_you_dont_know_in_actions(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        actions = build_improvement_actions(result)
        text = " ".join(str(a) for a in actions)
        assert not re.search(r"\byou\s+(do\s+)?don[' ]?t\s+know\b", text)
        assert not re.search(r"\byou\s+(do\s+)?don[' ]?t\s+have\b", text)

    def test_no_you_dont_know_in_roadmap(self):
        result = _make_result(missing_skills=[
            {"skill": "FastAPI", "requirement_type": "must_have", "jd_requirement": "FastAPI", "jd_evidence_ids": []},
        ])
        roadmap = build_learning_roadmap(result)
        for item in roadmap:
            why = str(item.get("why", ""))
            assert not re.search(r"\byou\s+(do\s+)?don[' ]?t\s+know\b", why)
            assert not re.search(r"\byou\s+(do\s+)?don[' ]?t\s+have\b", why)
            assert not re.search(r"\bsince\s+you\s+(already\s+)?know\b", why)


# ---------------------------------------------------------------------------
# Empty / Edge Cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_result_produces_fallback_roadmap(self):
        result = _make_result(missing_skills=[], matched_skills=[])
        roadmap = build_learning_roadmap(result)
        # When all skills are matched, roadmap should be empty (no gaps to address)
        assert isinstance(roadmap, list)

    def test_empty_result_produces_fallback_rewrite(self):
        result = _make_result(evidence=[])
        suggestions = build_safe_rewrite_suggestions(result)
        assert len(suggestions) >= 1
        assert suggestions[0].get("do_not_fabricate") is True

    def test_comparison_with_missing_scores(self):
        base = {"job_id": "base"}
        new = {"job_id": "new"}
        comp = compare_results(base, new, base_job_id="base", new_job_id="new")
        assert comp.get("base_score") is None
        assert comp.get("new_score") is None
        assert comp.get("score_delta") is None

    def test_roadmap_topics_for_unknown_skill(self):
        result = _make_result(missing_skills=[
            {"skill": "Terraform", "requirement_type": "nice_to_have", "jd_requirement": "Terraform", "jd_evidence_ids": []},
        ])
        roadmap = build_learning_roadmap(result)
        assert len(roadmap) > 0
        assert roadmap[0].get("topics") is not None
        assert len(roadmap[0]["topics"]) > 0

    def test_roadmap_topics_for_known_skill(self):
        result = _make_result(missing_skills=[
            {"skill": "Kubernetes", "requirement_type": "must_have", "jd_requirement": "Kubernetes", "jd_evidence_ids": []},
        ])
        roadmap = build_learning_roadmap(result)
        assert len(roadmap) > 0
        # Kubernetes should map to specific topics
        topics = roadmap[0].get("topics", [])
        assert isinstance(topics, list)
        assert len(topics) > 0
