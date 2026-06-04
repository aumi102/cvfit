from __future__ import annotations

from app.services.scoring.result_v2 import build_result_v2, fit_level


def jd_struct():
    return {
        "role": "Backend Engineer",
        "must_have_skill_groups": [["python"], ["fastapi"], ["postgresql"]],
        "nice_to_have_skill_groups": [["docker", "kubernetes"]],
        "responsibilities": ["Build APIs"],
        "skill_group_details": [
            {
                "group": ["python"],
                "type": "required",
                "source_line": "Required: Python backend development.",
            },
            {
                "group": ["fastapi"],
                "type": "required",
                "source_line": "Required: FastAPI service development.",
            },
            {
                "group": ["postgresql"],
                "type": "required",
                "source_line": "Required: PostgreSQL database experience.",
            },
            {
                "group": ["docker", "kubernetes"],
                "type": "preferred",
                "source_line": "Nice to have: Docker or Kubernetes deployment experience.",
            },
        ],
    }


def legacy_result(score=78.4):
    return {
        "job_id": "job-1",
        "scores": {
            "fit_score": score,
            "skill_match": 80,
            "responsibility_match": 75,
            "experience_level": 70,
            "project_relevance": 82,
            "cv_quality": 90,
        },
        "skills": {
            "matched_must_groups": [
                {"group": ["python"], "matched_by": "python"},
                {"group": ["fastapi"], "matched_by": "fastapi"},
            ],
            "matched_nice_groups": [
                {"group": ["docker", "kubernetes"], "matched_by": "docker"},
            ],
        },
        "skill_gap": {
            "missing_must_have": ["postgresql"],
            "missing_nice_to_have": ["kubernetes"],
            "learn_suggestions": [
                {
                    "skill": "postgresql",
                    "reason": "Required or useful in JD but not sufficiently evidenced in CV",
                    "resources_level": "beginner",
                    "time_estimate_weeks": 2,
                }
            ],
        },
        "responsibility_match": {
            "details": [
                {
                    "jd_requirement": "Build APIs",
                    "best_cv_bullet": "Built FastAPI services",
                    "similarity": 0.8,
                }
            ]
        },
        "cv_improvements": [
            {
                "issue": "Low number of measurable achievements",
                "fix": "add metrics such as latency or users",
            }
        ],
        "evidence": [
            {
                "type": "skill_match",
                "skill_group": ["fastapi"],
                "matched_skill": "fastapi",
                "text": "Built FastAPI services for internal users.",
            },
            {
                "type": "responsibility_match",
                "jd_requirement": "Build APIs",
                "text": "Built FastAPI services for internal users.",
                "similarity": 0.8,
            },
        ],
    }


def test_build_result_v2_preserves_legacy_fields():
    result = build_result_v2(legacy_result(), job_id="job-1")

    assert result["skills"]["matched_must_groups"][0]["matched_by"] == "python"
    assert result["skill_gap"]["missing_must_have"] == ["postgresql"]
    assert result["cv_improvements"][0]["issue"] == "Low number of measurable achievements"
    assert result["responsibility_match"]["details"][0]["jd_requirement"] == "Build APIs"


def test_build_result_v2_creates_required_fields():
    result = build_result_v2(
        legacy_result(),
        cv_parsed={"confidence": 0.85, "skills_detected": ["python", "fastapi"]},
        jd_struct=jd_struct(),
        job_id="job-1",
    )

    for key in (
        "schema_version",
        "fit_score",
        "overall",
        "score_breakdown",
        "matched_skills",
        "missing_skills",
        "evidence",
        "improvement_actions",
        "limitations",
        "metadata",
    ):
        assert key in result
    assert result["schema_version"] == "2.0"
    assert result["overall"]["fit_level"] == "good"
    assert result["overall"]["guardrail_notice"]
    assert result["metadata"]["scorer_version"] == "phase3.result_json_v2"


def test_fit_level_thresholds():
    assert fit_level(85) == "excellent"
    assert fit_level(84.9) == "good"
    assert fit_level(70) == "good"
    assert fit_level(69.9) == "partial"
    assert fit_level(50) == "partial"
    assert fit_level(49.9) == "weak"


def test_score_aliases_are_consistent():
    result = build_result_v2(legacy_result(score=88.5), job_id="job-1")

    assert result["fit_score"] == 88.5
    assert result["scores"]["fit_score"] == 88.5
    assert result["overall"]["fit_score"] == 88.5


def test_zero_score_aliases_are_preserved():
    result = build_result_v2(legacy_result(score=0.0), job_id="job-1")

    assert result["fit_score"] == 0.0
    assert result["scores"]["fit_score"] == 0.0
    assert result["overall"]["fit_score"] == 0.0
    assert result["overall"]["fit_level"] == "weak"


def test_jd_skill_group_evidence_is_created():
    result = build_result_v2(legacy_result(), jd_struct=jd_struct(), job_id="job-1")

    jd_skill_evidence = [
        item for item in result["evidence"] if item["source"] == "jd" and item["kind"] == "requirement"
    ]
    assert {item["id"] for item in jd_skill_evidence} >= {
        "ev_jd_skill_must_001",
        "ev_jd_skill_must_002",
        "ev_jd_skill_must_003",
        "ev_jd_skill_nice_001",
    }
    assert any(item["text"] == "Required: FastAPI service development." for item in jd_skill_evidence)


def test_missing_must_have_references_jd_evidence_id():
    result = build_result_v2(legacy_result(), jd_struct=jd_struct(), job_id="job-1")
    postgresql = next(item for item in result["missing_skills"] if item["skill"] == "postgresql")

    assert postgresql["requirement_type"] == "must_have"
    assert postgresql["severity"] == "high"
    assert postgresql["jd_requirement"] == "Required: PostgreSQL database experience."
    assert postgresql["jd_evidence_ids"] == ["ev_jd_skill_must_003"]
    assert "Only add this if it is true" in postgresql["suggestion"]


def test_matched_skill_references_cv_evidence_id():
    result = build_result_v2(legacy_result(), jd_struct=jd_struct(), job_id="job-1")
    fastapi = next(item for item in result["matched_skills"] if item["skill"] == "fastapi")

    assert fastapi["cv_evidence_ids"] == ["ev_cv_skill_001"]


def test_matched_skill_references_jd_evidence_id():
    result = build_result_v2(legacy_result(), jd_struct=jd_struct(), job_id="job-1")
    fastapi = next(item for item in result["matched_skills"] if item["skill"] == "fastapi")

    assert fastapi["jd_requirement"] == "Required: FastAPI service development."
    assert fastapi["jd_evidence_ids"] == ["ev_jd_skill_must_002"]


def test_responsibility_evidence_includes_jd_requirement_and_best_cv_bullet():
    result = build_result_v2(legacy_result(), jd_struct=jd_struct(), job_id="job-1")
    cv_resp = next(item for item in result["evidence"] if item["id"] == "ev_cv_resp_001")
    jd_resp = next(item for item in result["evidence"] if item["id"] == "ev_jd_resp_001")

    assert cv_resp["jd_requirement"] == "Build APIs"
    assert cv_resp["best_cv_bullet"] == "Built FastAPI services for internal users."
    assert cv_resp["similarity"] == 0.8
    assert cv_resp["jd_evidence_ids"] == ["ev_jd_resp_001"]
    assert jd_resp["text"] == "Build APIs"


def test_missing_skill_wording_uses_parsed_cv_language():
    result = build_result_v2(legacy_result(), jd_struct=jd_struct(), job_id="job-1")

    reasons = " ".join(item["reason"] for item in result["missing_skills"])
    summary = result["overall"]["summary"]
    assert "not found in the parsed CV" in reasons
    assert "not found in the parsed CV" in summary
    assert "you do not know" not in reasons.lower()
    assert "you do not have" not in reasons.lower()


def test_improvement_actions_are_conditional_and_guardrailed():
    result = build_result_v2(legacy_result(), jd_struct=jd_struct(), job_id="job-1")

    suggestions = " ".join(item["suggestion"] for item in result["improvement_actions"])
    guardrails = " ".join(item["guardrail"] for item in result["improvement_actions"])
    assert "If you have actually used" in suggestions
    assert "Only add this if it is true" in suggestions
    assert "Do not invent" in guardrails


def test_missing_must_have_improvement_action_is_high_priority_and_conditional():
    result = build_result_v2(legacy_result(), jd_struct=jd_struct(), job_id="job-1")
    action = next(item for item in result["improvement_actions"] if item["related_skill"] == "postgresql")

    assert action["priority"] == "high"
    assert action["related_evidence_ids"] == ["ev_jd_skill_must_003"]
    assert "If you have actually used postgresql" in action["suggestion"]
    assert "Only add this if it is true" in action["suggestion"]
    assert "Do not invent" in action["guardrail"]


def test_limitations_include_no_hiring_guarantee():
    result = build_result_v2(legacy_result(), job_id="job-1")

    assert any("does not guarantee any hiring outcome" in item for item in result["limitations"])


def test_sensitive_keys_are_not_exposed():
    unsafe = legacy_result()
    unsafe.update(
        {
            "access_token": "secret-token",
            "access_token_hash": "secret-hash",
            "storage_path": "uploads/private-cv.docx",
            "report_docx_path": "reports/private.docx",
            "raw_cv_text": "full private cv",
            "nested": {
                "local_path": "C:/private/cv.docx",
                "s3_key": "private/key",
                "safe": "ok",
            },
        }
    )

    result = build_result_v2(unsafe, jd_struct=jd_struct(), job_id="job-1")
    text = str(result)

    assert result["nested"] == {"safe": "ok"}
    assert "secret-token" not in text
    assert "secret-hash" not in text
    assert "uploads/private-cv.docx" not in text
    assert "reports/private.docx" not in text
    assert "full private cv" not in text
    assert "C:/private/cv.docx" not in text
    assert "private/key" not in text
