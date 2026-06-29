# AI CV Fit App — Expanded Phase 4 Team Plan

**Ngày cập nhật:** 2026-06-06  
**Team:** Phúc — Quân — Đạt  
**Trạng thái đầu vào:** Phase 3 đã hoàn thành và đã qua review/audit.  
**Phase 4 expanded theme:** **Career Readiness Operating System — Improve CV, Compare Progress, Prepare Interview, Plan Learning**

---

## 1. Tư duy mở rộng Phase 4

Bản Phase 4 trước tập trung vào:

```text
Guided CV Improvement Loop
Before/After Comparison
Safe Action Plan
```

Bản Phase 4 mở rộng này vẫn giữ trục đó, nhưng thêm nhiều lớp sản phẩm hơn để AI CV Fit App không chỉ là công cụ chấm điểm CV, mà trở thành một hệ thống hỗ trợ ứng viên đi từ:

```text
Tôi có CV
→ Tôi muốn ứng tuyển JD này
→ Tôi biết mình fit bao nhiêu
→ Tôi biết thiếu gì
→ Tôi biết sửa CV thế nào
→ Tôi sửa lại và đo lại
→ Tôi luyện phỏng vấn theo gap
→ Tôi có roadmap học tiếp
→ Tôi có report/plan để theo dõi tiến bộ
```

Phase 4 mở rộng nên định vị là:

> **Career Readiness Operating System cho sinh viên/fresher: CV fit analysis + improvement loop + interview prep + learning roadmap + progress tracking.**

---

## 2. Phase 4 Expanded Objective

Phase 4 có mục tiêu xây một vòng lặp hoàn chỉnh:

1. Phân tích CV với JD.
2. Trả result có evidence.
3. Sinh improvement action plan.
4. Cho phép user upload CV đã sửa.
5. So sánh before/after.
6. Chỉ ra improvement thật và improvement giả.
7. Sinh interview prep dựa trên gaps.
8. Sinh learning roadmap dựa trên missing skills.
9. Hỗ trợ safe CV rewrite snippets.
10. Cập nhật dashboard/report để demo như một sản phẩm end-to-end.

---

## 3. Product Pillars của Phase 4

Phase 4 sẽ có 6 pillar chính:

## Pillar 1 — Improvement Action Plan

Từ Result JSON v2, hệ thống sinh action cụ thể:

- Cần bổ sung evidence nào.
- Cần làm rõ project nào.
- Cần thêm skill nào nếu user thật sự có.
- Cần cải thiện wording nào.
- Cần thêm metric/outcome nào.

Mỗi action có:

```text
id
priority
category
title
reason
linked_skill
linked_evidence
safe_suggestion
status
```

Status:

```text
open
resolved
still_missing
not_applicable
```

---

## Pillar 2 — Before/After CV Comparison

User upload CV version mới cho cùng JD và xem:

- score tăng/giảm bao nhiêu,
- skill nào đã được resolved,
- skill nào vẫn missing,
- evidence mới nào được tìm thấy,
- action nào đã được xử lý,
- có dấu hiệu keyword stuffing không,
- CV mới có thật sự tốt hơn không.

---

## Pillar 3 — Safe CV Rewrite Assistant v1

Không viết lại CV tự do kiểu bịa kinh nghiệm.

Chỉ làm safe rewrite ở mức:

- gợi ý cấu trúc bullet,
- rewrite từ nội dung user đã có,
- nhắc user chỉ thêm skill nếu thật sự có,
- gợi ý làm rõ impact/metric,
- phân biệt rõ:
  - found evidence,
  - missing evidence,
  - suggested wording.

Ví dụ output an toàn:

```text
Current evidence found:
"Built a backend API for job tracking."

Safer rewrite suggestion:
"Built a backend API for job tracking using [framework you actually used], with PostgreSQL for data storage and async job processing."

Note:
Only mention FastAPI/Celery/Redis if you actually used them in this project.
```

---

## Pillar 4 — Interview Prep v1

Từ CV + JD + missing skills, sinh bộ câu hỏi phỏng vấn:

- technical questions,
- project deep-dive questions,
- behavioral questions,
- gap-checking questions,
- follow-up questions.

Mỗi câu hỏi cần có:

```text
question
type
why_this_question
related_jd_requirement
related_cv_evidence
suggested_answer_outline
risk_if_user_cannot_answer
```

Không cần làm full AI interview engine ở Phase 4. Chỉ cần interview prep pack.

---

## Pillar 5 — Learning Roadmap v1

Từ missing skills và weak evidence, tạo roadmap:

- skill cần học,
- vì sao cần học,
- mức ưu tiên,
- learning topics,
- mini project suggestion,
- estimated effort,
- evidence to add to CV after learning.

Ví dụ:

```text
Missing skill: FastAPI
Priority: High
Why: JD explicitly asks for backend API development with FastAPI.
Learning topics:
- FastAPI routing
- Pydantic schemas
- SQLAlchemy integration
- Auth/JWT basics
Mini project:
Build a CV analysis API endpoint and document it in your CV.
CV evidence after completion:
Add one bullet describing the API, database, deployment and outcome.
```

---

## Pillar 6 — Progress Tracking / Application Readiness

User có thể xem:

- các lần phân tích theo cùng JD,
- score theo thời gian,
- resolved gaps,
- remaining gaps,
- interview readiness status,
- learning roadmap progress.

MVP có thể chỉ cần hiển thị trong history/job detail, chưa cần dashboard lớn.

---

## 4. Expanded In-scope Features

## 4.1 Must-have

Các việc bắt buộc để chốt Phase 4 mở rộng:

1. Improvement Action Plan v1.
2. Re-analysis flow.
3. Before/After Comparison.
4. Comparison Dashboard.
5. Safe rewrite snippets v1.
6. Interview Prep Pack v1.
7. Learning Roadmap v1.
8. Guardrails v2.
9. Before/after evaluation dataset.
10. Keyword stuffing detection basic.
11. Report DOCX v3.
12. History integration for revisions/comparison.
13. Render smoke vẫn pass.
14. Không phá auth/history/result v2.

---

## 4.2 Should-have

1. Progress tracking UI.
2. Comparison report export.
3. Interview prep section trong DOCX.
4. Learning roadmap section trong DOCX.
5. Manual action checklist UI.
6. Role readiness summary.
7. Basic debug view cho internal QA:
   - parsed CV text,
   - parsed JD skills,
   - score breakdown,
   - evidence mapping.
   Chỉ dùng nội bộ/dev, không public nếu chưa bảo vệ.

---

## 4.3 Could-have

1. Shareable read-only report link với token riêng.
2. Email report to user.
3. Multiple CV version timeline.
4. Compare 3+ versions.
5. Interview answer self-rating.
6. Export learning roadmap as markdown/PDF.
7. Demo mode with sample CV/JD.

---

## 4.4 Explicitly Out-of-scope

Không làm trong Phase 4:

1. Payment/subscription.
2. Recruiter multi-tenant dashboard.
3. Job board crawling.
4. Full AI interview voice/chat engine.
5. Full CV editor like Google Docs.
6. Auto rewrite toàn bộ CV không kiểm soát.
7. Public share links without security review.
8. Browser extension.
9. Mobile app.
10. Enterprise admin system.

---

## 5. Expanded User Flow

## 5.1 Logged-in User Flow

```text
Login
→ Upload CV + paste JD
→ View Result Dashboard v2
→ View Improvement Action Plan
→ View Safe Rewrite Suggestions
→ View Interview Prep Pack
→ View Learning Roadmap
→ Edit CV offline
→ Upload revised CV for same JD
→ Run new analysis
→ View Before/After Comparison
→ Track resolved/still missing gaps
→ Download DOCX Report v3
→ Save all versions in history
```

---

## 5.2 Guest User Flow

```text
Upload CV + paste JD
→ View result using access_token
→ View improvement actions
→ Upload revised CV in same browser session
→ Compare before/after using access_token
→ Download report
```

Guest mode không cần long-term progress tracking.

---

## 6. Technical Architecture Impact

Phase 4 mở rộng nên vẫn giữ architecture hiện tại, chỉ thêm lớp service rõ ràng.

## 6.1 Backend service modules đề xuất

```text
backend/app/services/improvement/
  action_plan.py
  safe_rewrite.py

backend/app/services/comparison/
  compare_results.py
  keyword_stuffing.py

backend/app/services/interview/
  interview_prep.py

backend/app/services/roadmap/
  learning_roadmap.py
```

Không nhất thiết phải có đúng cấu trúc này, nhưng nên tách logic để tránh `scorer.py` phình quá lớn.

---

## 6.2 DB/schema additions đề xuất

Tối thiểu:

```text
analysis_jobs.parent_job_id nullable
analysis_jobs.analysis_group_id nullable
analysis_jobs.revision_number integer
```

Có thể thêm nếu cần:

```text
analysis_artifacts
  id
  job_id
  artifact_type
  payload_json
  created_at
```

artifact_type:

```text
improvement_action_plan
interview_prep
learning_roadmap
comparison_result
```

Nếu muốn giữ đơn giản, có thể lưu các artifact này trong `result_json` trước.

Khuyến nghị Phase 4:

- Dùng `result_json` cho action/interview/roadmap v1.
- Thêm linking fields cho before/after.
- Chưa tạo quá nhiều bảng nếu không cần.

---

## 6.3 API endpoints đề xuất

## Re-analysis

```text
POST /v1/jobs/{job_id}/reanalyze
```

Input:

```json
{
  "cv_file_id": "...",
  "jd_text": null
}
```

Output:

```json
{
  "job_id": "...",
  "access_token": "...",
  "parent_job_id": "...",
  "revision_number": 2
}
```

---

## Comparison

```text
GET /v1/jobs/{job_id}/comparison/{other_job_id}
```

Output:

```json
{
  "base_job_id": "...",
  "new_job_id": "...",
  "score_delta": 12.4,
  "breakdown_delta": {
    "skill_match": 8,
    "experience_match": 5
  },
  "resolved_missing_skills": [],
  "still_missing_skills": [],
  "newly_matched_skills": [],
  "keyword_stuffing_warnings": [],
  "next_actions": []
}
```

---

## Interview Prep

Có thể làm theo 2 cách:

### Option A — part of result JSON

Không thêm endpoint riêng. Result trả thêm:

```json
{
  "interview_prep": [...]
}
```

### Option B — endpoint riêng

```text
GET /v1/jobs/{job_id}/interview-prep
```

Khuyến nghị Phase 4: bắt đầu với Option A để giảm API surface.

---

## Learning Roadmap

Tương tự interview prep, có thể nằm trong result JSON:

```json
{
  "learning_roadmap": [...]
}
```

Khuyến nghị Phase 4: bắt đầu trong result JSON.

---

## 7. Expanded Result JSON v3 Proposal

Phase 4 có thể mở rộng result thành v3 nhưng giữ compatibility với v2.

```json
{
  "overall": {
    "fit_score": 75.9,
    "fit_level": "good",
    "summary": "CV matches many backend requirements but lacks clear FastAPI evidence."
  },
  "score_breakdown": {
    "skill_match": 82,
    "experience_match": 70,
    "responsibility_match": 76,
    "project_relevance": 78,
    "cv_quality": 72
  },
  "matched_skills": [],
  "missing_skills": [],
  "improvement_actions": [
    {
      "id": "action_skill_fastapi",
      "priority": "high",
      "category": "missing_skill_evidence",
      "status": "open",
      "linked_skill": "FastAPI",
      "reason": "JD requires FastAPI but no evidence was found.",
      "safe_suggestion": "If you have FastAPI experience, add a concrete backend API project bullet.",
      "do_not_fabricate": true
    }
  ],
  "safe_rewrite_suggestions": [
    {
      "source_evidence": "Built a backend API for job tracking.",
      "suggested_structure": "Built [type of API] using [actual framework] with [actual database] to achieve [actual outcome].",
      "warning": "Only mention tools you actually used."
    }
  ],
  "interview_prep": [
    {
      "question": "Can you explain the backend API project listed in your CV?",
      "type": "project_deep_dive",
      "why_this_question": "The JD expects backend API experience.",
      "related_jd_requirement": "Backend API development",
      "related_cv_evidence": "Built a backend API for job tracking.",
      "suggested_answer_outline": [
        "Problem",
        "Architecture",
        "Tools actually used",
        "Database",
        "Deployment",
        "Outcome"
      ],
      "risk_if_user_cannot_answer": "May indicate weak evidence behind the CV claim."
    }
  ],
  "learning_roadmap": [
    {
      "skill": "FastAPI",
      "priority": "high",
      "why": "JD asks for FastAPI, but no CV evidence was found.",
      "topics": ["routing", "schemas", "database integration", "auth"],
      "mini_project": "Build a small CV analysis API using FastAPI and PostgreSQL.",
      "cv_evidence_to_add_after_learning": "Add a project bullet only after building it."
    }
  ],
  "limitations": [
    "This analysis is an estimate and does not guarantee hiring outcomes.",
    "Do not add skills or experience to your CV unless they are true."
  ]
}
```

---

# 8. Team Assignment

---

# 8.1 Phúc — Backend/Product/Architecture Lead

## Vai trò

Phúc chịu trách nhiệm mở rộng product contract, backend services, comparison logic, action/interview/roadmap generation, migration, deploy và final integration.

## Main Responsibilities

1. Phase 4 expanded product/API contract.
2. Result JSON v3 compatibility.
3. Improvement Action Plan backend.
4. Safe Rewrite Suggestions backend.
5. Interview Prep Pack backend.
6. Learning Roadmap backend.
7. Re-analysis endpoint.
8. Comparison endpoint.
9. DB linking for revisions.
10. Report DOCX v3 backend data.
11. Render smoke/release.

## Files/Folders likely touched

```text
backend/app/api/routes/jobs.py
backend/app/schemas/
backend/app/services/scoring/
backend/app/services/improvement/
backend/app/services/comparison/
backend/app/services/interview/
backend/app/services/roadmap/
backend/app/services/reporting/
backend/app/db/models.py
backend/alembic/versions/
scripts/smoke_test_local.py
scripts/smoke_test_s3.py
docs/result_schema_v3.md
docs/comparison_api_contract.md
docs/phase4_team_plan.md
README.md
```

## Deliverables

1. `docs/result_schema_v3.md`
2. `docs/comparison_api_contract.md`
3. Backend improvement action plan v1.
4. Safe rewrite suggestions v1.
5. Interview prep pack v1.
6. Learning roadmap v1.
7. Re-analysis endpoint.
8. Comparison endpoint.
9. Migration for revision linking if needed.
10. DOCX report v3 backend support.
11. Render smoke pass.

## Acceptance Criteria

- Result remains backward compatible with v2.
- Existing dashboard/auth/history does not break.
- User can generate improvement actions.
- User can get interview prep pack.
- User can get learning roadmap.
- User can re-analyze a revised CV.
- User can compare before/after.
- Comparison includes score delta and resolved/still missing gaps.
- Report download still works.
- No fake experience is generated.
- Tests/smoke pass.

## Dependencies

- Quân depends on Phúc for schema/API contracts.
- Đạt depends on Phúc for output shape and comparison logic.
- Phúc needs evaluation cases from Đạt to tune guardrails.

---

# 8.2 Quân — Frontend/UX Owner

## Vai trò

Quân chịu trách nhiệm biến expanded Phase 4 thành trải nghiệm sản phẩm rõ ràng và demo tốt.

## Main Responsibilities

1. Improvement action plan UI.
2. Safe rewrite suggestions UI.
3. Interview prep pack UI.
4. Learning roadmap UI.
5. Re-analysis upload UI.
6. Before/after comparison dashboard.
7. Progress/history integration.
8. Empty/error/loading states.

## Files/Folders likely touched

```text
frontend/
frontend/app/
frontend/components/
frontend/components/results/
frontend/components/improvement/
frontend/components/comparison/
frontend/components/interview/
frontend/components/roadmap/
frontend/components/history/
frontend/lib/api.ts
frontend/lib/auth.ts
```

## UI Modules

### A. ImprovementActionPlan

Hiển thị:

- priority,
- action title,
- reason,
- linked skill,
- safe suggestion,
- status.

### B. SafeRewriteSuggestions

Hiển thị:

- current evidence,
- suggested bullet structure,
- warning “only include true experience”.

### C. InterviewPrepPack

Hiển thị:

- question,
- type,
- why this question,
- suggested answer outline,
- related CV/JD evidence.

### D. LearningRoadmap

Hiển thị:

- missing skill,
- why important,
- topics,
- mini project,
- CV evidence to add after learning.

### E. ReAnalyzeUpload

Cho user upload revised CV và chạy lại analysis.

### F. ComparisonDashboard

Hiển thị:

- previous score,
- new score,
- delta,
- resolved gaps,
- still missing gaps,
- newly matched skills,
- keyword stuffing warnings,
- next actions.

## Deliverables

1. Improvement action plan section.
2. Safe rewrite section.
3. Interview prep section.
4. Learning roadmap section.
5. Re-analyze upload flow.
6. Before/after comparison dashboard.
7. History integration for revisions/compare.
8. Error/empty/loading states.

## Acceptance Criteria

- User hiểu cần sửa CV thế nào.
- User thấy warning không bịa kinh nghiệm.
- User có câu hỏi phỏng vấn để chuẩn bị.
- User có roadmap học skill còn thiếu.
- User upload revised CV được.
- User thấy before/after comparison rõ.
- UI không leak access token/JWT.
- Auth/history/report download không vỡ.

## Dependencies

- Cần Phúc chốt Result JSON v3/API contract.
- Cần Đạt cung cấp edge cases để test UI.
- Cần backend comparison endpoint trước khi full integration.

---

# 8.3 Đạt — Evaluation/Guardrails/QA Owner

## Vai trò

Đạt chịu trách nhiệm chứng minh expanded Phase 4 hoạt động hợp lý, không hallucinate/fabricate và không bị keyword stuffing đánh lừa quá dễ.

## Main Responsibilities

1. Before/after evaluation dataset.
2. Keyword stuffing cases.
3. Interview prep quality checks.
4. Learning roadmap quality checks.
5. Safe rewrite guardrails tests.
6. Comparison tests.
7. Regression tests.
8. Guardrails v2 docs.
9. Phase 4 evaluation report.

## Files/Folders likely touched

```text
evaluation/
evaluation/cases/before_after/
evaluation/cases/interview_prep/
evaluation/cases/learning_roadmap/
scripts/evaluate_comparison_cases.py
scripts/evaluate_interview_prep_cases.py
scripts/evaluate_roadmap_cases.py
backend/tests/
docs/guardrails_v2.md
docs/phase4_evaluation_report.md
```

## Evaluation Dataset Requirements

### Before/After

Tối thiểu:

1. 5 cases score nên tăng.
2. 3 cases score không nên tăng nhiều vì sửa không liên quan.
3. 3 cases keyword stuffing.
4. 2 cases CV after dài hơn nhưng evidence vẫn yếu.
5. 2 cases resolved skill evidence thật.

### Interview Prep

Tối thiểu:

1. 5 cases câu hỏi đúng với JD.
2. 3 cases câu hỏi project deep-dive.
3. 3 cases gap-checking questions.
4. 2 cases tránh hỏi sai vì CV không có evidence.

### Learning Roadmap

Tối thiểu:

1. 5 missing skill roadmap cases.
2. 3 low-priority skill cases.
3. 3 cases roadmap không được claim user đã có skill.
4. 2 cases mini project suggestion.

## Tests cần có

1. Result JSON v3 has required fields.
2. Improvement actions are safe.
3. Safe rewrite does not fabricate.
4. Interview questions include why/related evidence.
5. Learning roadmap does not claim missing skills as existing.
6. Comparison computes score delta.
7. Resolved gaps require real evidence.
8. Keyword stuffing warning appears.
9. Wrong user/token cannot compare.
10. Report v3 generation does not fail.
11. Smoke scripts do not leak token-bearing URLs.

## Guardrails v2

Tạo/cập nhật:

```text
docs/guardrails_v2.md
```

Nội dung:

- No fabricated experience.
- No fabricated skill.
- No hiring guarantee.
- Evidence-first suggestions.
- Safe rewrite rules.
- Interview prep caveats.
- Learning roadmap caveats.
- Keyword stuffing warning.
- Token/privacy logging rules.

## Deliverables

1. Before/after evaluation dataset.
2. Interview prep evaluation cases.
3. Learning roadmap evaluation cases.
4. Evaluation scripts.
5. Guardrails v2 docs.
6. Tests for safe outputs.
7. Phase 4 evaluation report.

## Acceptance Criteria

- Có ít nhất 25 total evaluation cases.
- Evaluation scripts chạy được.
- Tests pass.
- Keyword stuffing không được coi là improvement thật.
- Safe rewrite không bịa.
- Interview prep không hỏi bừa ngoài evidence/JD.
- Learning roadmap không claim user đã có skill.
- Guardrails v2 được document rõ.

---

## 9. Expanded Timeline Proposal

## Day 1 — Contracts & Skeletons

### Phúc
- Tạo `docs/result_schema_v3.md`.
- Tạo `docs/comparison_api_contract.md`.
- Chốt scope API/backend.

### Quân
- Tạo UI skeleton:
  - action plan,
  - rewrite suggestions,
  - interview prep,
  - learning roadmap,
  - comparison.

### Đạt
- Tạo evaluation folders.
- Viết first batch before/after cases.
- Draft guardrails v2.

---

## Day 2 — Backend Expansion v1

### Phúc
- Implement improvement action plan.
- Implement safe rewrite suggestions.
- Extend result JSON v3 while keeping v2 compatibility.

### Quân
- Render improvement actions.
- Render safe rewrite suggestions.

### Đạt
- Tests for action/safe rewrite.
- Keyword stuffing cases.

---

## Day 3 — Interview & Roadmap

### Phúc
- Implement interview prep pack.
- Implement learning roadmap pack.

### Quân
- Render interview prep section.
- Render learning roadmap section.

### Đạt
- Evaluation cases for interview prep.
- Evaluation cases for roadmap.

---

## Day 4 — Re-analysis & Comparison

### Phúc
- Implement reanalysis endpoint.
- Implement comparison endpoint.
- Add migration if needed.

### Quân
- Implement re-upload UI.
- Implement comparison dashboard.

### Đạt
- Comparison tests.
- Before/after evaluation script.

---

## Day 5 — Report v3 & Integration

### Phúc
- Update DOCX report v3.
- Update smoke scripts if needed.

### Quân
- Polish full UX.
- Empty/error states.

### Đạt
- Guardrails v2 final.
- Run evaluation suite.
- Write evaluation report.

---

## Day 6 — Closeout

### Cả team
- Merge PRs.
- Run tests.
- Local smoke.
- Render smoke.
- Update README/docs.
- Prepare demo script and screenshots.

---

## 10. Updated Definition of Done

Phase 4 mở rộng hoàn thành khi:

1. Result JSON v3 hoặc v2 extension có contract rõ.
2. Improvement action plan hoạt động.
3. Safe rewrite suggestions hoạt động và không bịa kinh nghiệm.
4. Interview prep pack hoạt động.
5. Learning roadmap hoạt động.
6. User upload revised CV được.
7. Backend tạo linked analysis job.
8. User compare before/after được.
9. Comparison có score delta.
10. Comparison có resolved/still missing gaps.
11. Frontend hiển thị action plan.
12. Frontend hiển thị safe rewrite.
13. Frontend hiển thị interview prep.
14. Frontend hiển thị learning roadmap.
15. Frontend hiển thị comparison dashboard.
16. History page hỗ trợ compare/revisions.
17. Guardrails v2 có.
18. Có ít nhất 25 evaluation cases.
19. Evaluation scripts chạy được.
20. Tests pass.
21. Local smoke pass.
22. Render smoke pass.
23. Report DOCX v3 hoặc report extension có.
24. Auth/history flow không vỡ.
25. Không khuyến khích bịa kinh nghiệm.
26. Không xem keyword stuffing là improvement thật.
27. README/docs cập nhật.

---

## 11. First PR Sequence

## PR 1 — Expanded Phase 4 Contract Docs Only

Owner: Phúc

Files:

```text
docs/phase4_team_plan.md
docs/result_schema_v3.md
docs/comparison_api_contract.md
docs/guardrails_v2.md draft
```

Vì sao làm đầu tiên:

- Quân cần schema để build UI.
- Đạt cần schema để viết evaluation/tests.
- Backend cần contract để tránh đổi lung tung.
- Không đổi product logic.

---

## PR 2 — Evaluation Skeleton

Owner: Đạt

Files:

```text
evaluation/cases/before_after/
evaluation/cases/interview_prep/
evaluation/cases/learning_roadmap/
scripts/evaluate_comparison_cases.py
```

---

## PR 3 — Backend Result Expansion

Owner: Phúc

Files:

```text
backend/app/services/improvement/
backend/app/services/interview/
backend/app/services/roadmap/
backend/app/services/scoring/
backend/app/schemas/
```

---

## PR 4 — Frontend Expanded Result UI

Owner: Quân

Files:

```text
frontend/
```

---

## PR 5 — Reanalysis + Comparison

Owner: Phúc

Files:

```text
backend/app/api/routes/jobs.py
backend/app/db/models.py
backend/alembic/versions/
frontend/components/comparison/
```

---

## PR 6 — Report v3 + Guardrails + Final Closeout

Owner: cả team

---

## 12. Risks & Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Scope quá rộng | Trễ phase | Tách must/should/could, PR nhỏ |
| Safe rewrite thành bịa CV | Rủi ro lớn | Guardrails + evaluation cases |
| Interview prep hallucinate | User mất tin tưởng | Câu hỏi phải dựa trên JD/evidence/gap |
| Roadmap claim user đã có skill | Sai product | Wording: missing/learning, không claim |
| Keyword stuffing làm score tăng | Sản phẩm yếu | Cases keyword stuffing + warning |
| Frontend quá tải nhiều section | UX rối | Accordion/tabs |
| Backend scorer phình to | Maintainability kém | Tách services |
| DB migration lỗi Render | Deploy lỗi | Migration nhỏ, test disposable DB |
| Token leak | Privacy risk | Redact logs, không print token |
| Report v3 quá lâu | Trễ | Report v3 should-have nếu UI đã đủ tốt |

---

## 13. Validation Commands

Sau mỗi PR lớn:

```bash
python -m compileall backend/app
cd backend && python -m pytest --basetemp pytest-cache-files-local -p no:cacheprovider
docker compose config
python scripts/smoke_test_local.py
```

Sau deploy:

```bash
set "API_BASE_URL=https://cvfit.onrender.com"
python scripts/smoke_test_s3.py
```

---

## 14. Immediate Next Actions

1. Phúc tạo branch:
   ```bash
   git checkout -b phase4/phuc-expanded-contract
   ```
2. Phúc tạo:
   ```text
   docs/result_schema_v3.md
   docs/comparison_api_contract.md
   ```
3. Quân tạo branch:
   ```bash
   git checkout -b phase4/quan-expanded-ui
   ```
4. Đạt tạo branch:
   ```bash
   git checkout -b phase4/dat-expanded-evaluation
   ```
5. Không bắt đầu code lớn trước khi PR contract được merge.
