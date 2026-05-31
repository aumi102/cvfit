# Phase 2 Product Spec — AI CV Fit

Theme: Product MVP Polish + Differentiation

## Positioning

AI CV Fit không chỉ là resume scanner.  
Nó là Career Readiness Coach cho sinh viên/fresher Việt Nam:

```text
CV Fit Score
+ Role Readiness Score
+ Evidence-based Feedback
+ Interview Readiness
+ Skill Gap Roadmap
+ CV Improvement Tracking
```

## Phase 2 goals

1. Làm result dashboard dễ hiểu, đẹp, có hành động tiếp theo.
2. Feedback phải explainable/evidence-based.
3. Chuẩn bị login/history nhưng không phá guest mode.
4. Tạo lợi thế so với tool chỉ scan keyword/ATS.
5. Tăng độ tin cậy bằng guardrails, logs, tests.

## Feature group 1 — Result Dashboard

### Must-have

- Overall Fit Score.
- Skill Match.
- Missing Skills.
- Experience Match.
- Project Relevance.
- ATS/readability warnings.
- Top 5 actions to improve.
- Download report.

### Suggested UI sections

```text
1. Overall Readiness
2. Skill Match Matrix
3. Evidence Found in CV
4. Missing / Weak Evidence
5. Recommended Fixes
6. Interview Preparation
```

## Feature group 2 — Evidence-based Feedback

Mỗi nhận xét phải có cấu trúc:

```json
{
  "claim": "Candidate has backend Python experience",
  "jd_requirement": "Python, FastAPI, PostgreSQL",
  "cv_evidence": "Built FastAPI app with PostgreSQL in project X",
  "status": "found | partial | missing",
  "confidence": 0.82
}
```

Rule:
- Không chỉ nói “thiếu kỹ năng”.
- Phải chỉ ra JD yêu cầu gì, CV có gì, thiếu gì.
- Nếu không thấy evidence, nói “not found in CV”, không kết luận user không biết skill đó.

## Feature group 3 — CV Rewrite Assistant

### Scope

Cho phép rewrite bullet points dựa trên nội dung user đã có.

### Guardrails

- Không bịa công ty, role, kỹ năng, số liệu.
- Không tự thêm kinh nghiệm chưa có.
- Nếu thiếu skill, gợi ý học/bổ sung nếu đúng sự thật.
- Mọi rewrite phải có mode “before/after”.

### Prompt rule

```text
Rewrite only from provided CV facts. Do not invent skills, employers, metrics, certifications, dates, or experience.
```

## Feature group 4 — Interview Readiness

Sinh câu hỏi từ CV + JD:

- 3 technical questions.
- 3 project/experience questions.
- 2 behavioral questions.
- 2 gap-checking questions.

Chấm câu trả lời theo:

- clarity,
- relevance,
- evidence,
- confidence,
- missing points.

## Feature group 5 — Career Roadmap

Dựa trên missing skills:

- 1-week plan,
- 2-week plan,
- 1-month plan,
- project suggestions,
- learning topics,
- interview practice tasks.

## Feature group 6 — User History

Sau login:

- lưu CV,
- lưu JD,
- lưu analysis,
- lưu report,
- so sánh score trước/sau khi sửa CV,
- resume improvement timeline.

## Feature group 7 — Recruiter mode, sau MVP polish

Không làm ngay trước khi dashboard candidate ổn.

Later:
- job posting,
- candidate list,
- candidate comparison,
- screening notes,
- interview readiness threshold.

## Phase 2 acceptance criteria

- User hiểu “vì sao score như vậy”.
- Mỗi recommendation có evidence hoặc missing-evidence label.
- Có ít nhất 5 sample CV/JD để test dashboard.
- Không có hallucinated rewrite trong test cases.
- Có basic auth hoặc guest-history strategy được quyết định bằng ADR.
