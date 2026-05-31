<!-- 00_README_START_HERE.md -->

# AI CV Fit — Phase 1 Closeout & Phase 2 Preparation Pack

Ngày tạo: 27/05/2026  
Mục tiêu: giúp Phúc đóng vai trò product/tech lead trong lúc chờ Quân làm Next frontend và Đạt hoàn tất phần backend/devops.

## Thứ tự làm đề xuất

1. Chốt scope Phase 1: demo ổn, deploy ổn, token bảo vệ result/report, docs rõ.
2. Tạo checklist Phase 1 và chia owner rõ: Phúc / Quân / Đạt.
3. Gửi API contract cho Quân.
4. Smoke test backend Render + S3 + access token.
5. Validate Alembic trên DB local/disposable trước khi đụng DB production.
6. Thêm S3 lifecycle cleanup policy.
7. Viết Phase 2 Product Spec theo theme: Product MVP Polish + Differentiation.
8. Viết Guardrails Spec: file upload, privacy, output, rewrite guardrails.
9. Chuẩn bị demo script + fallback plan: nếu Next chưa ổn thì giữ Jinja UI để demo.

## Scope khóa trước thứ Bảy 30/05/2026

Nên làm:
- Access token MVP cho result/report.
- API contract cho Next frontend.
- Smoke test end-to-end.
- Alembic validation.
- S3 cleanup.
- Docs/runbook.
- Phase 2 roadmap/spec.

Không nên làm ngay:
- Full login/account system.
- Recruiter dashboard đầy đủ.
- Payment.
- Job board integration.
- AI interview phức tạp.
- CV rewrite mạnh nếu chưa có guardrail chống bịa.


---

<!-- 01_phase1_closeout_checklist.md -->

# Phase 1 Closeout Checklist — AI CV Fit

Deadline nội bộ: Thứ Bảy, 30/05/2026  
Nguyên tắc: không chốt bằng cảm tính; mỗi mục cần có evidence.

| Nhóm việc | Task | Owner | Status | Evidence cần có | Blocker | Must-have before close? | Can move Phase 2? |
|---|---|---:|---|---|---|---|---|
| Deploy | Render backend chạy ổn | Phúc | TODO | `/health` OK, logs không crash | Env / build / start command | Yes | No |
| Deploy | Worker chạy ổn | Phúc/Đạt | TODO | queue job chạy từ queued → running → succeeded/failed rõ | Redis/Celery/env | Yes | No |
| Storage | S3 upload/download smoke | Phúc | TODO | upload CV thành công, report download được | AWS credentials, bucket, region | Yes | No |
| Security MVP | Access token bảo vệ result/report | Phúc/Đạt | TODO | không token → 401/403; token đúng → 200; token sai → 401/403 | API chưa enforce | Yes | No |
| API Contract | Contract cho Next frontend | Phúc | TODO | `docs/api-contract-next.md` merge vào repo | Endpoint chưa thống nhất | Yes | No |
| Frontend | Next landing page | Quân | TODO | mở được page deploy/local | Design/API mismatch | Yes | No, nếu Jinja fallback |
| Frontend | Analyze page: upload CV + paste JD | Quân | TODO | gửi request thật tới backend | CORS/API contract | Yes | No, nếu Jinja fallback |
| Frontend | Loading/result/download flow | Quân + Phúc | TODO | job polling + result + download OK | access_token handling | Yes | No, nếu Jinja fallback |
| Migration | Alembic baseline validation | Đạt/Phúc | TODO | disposable DB chạy `alembic upgrade head` OK | migration drift | Yes | No |
| Cleanup | S3 lifecycle cleanup | Phúc/Đạt | TODO | lifecycle policy JSON hoặc console screenshot | quyền AWS | Should | Yes, nếu có runbook |
| Docs | Runbook smoke test | Phúc | TODO | `docs/runbook-phase1.md` có lệnh chạy | thiếu endpoint/env | Yes | No |
| Product | Phase 2 Product Spec | Phúc | TODO | `docs/phase2-product-spec.md` | chưa thống nhất scope | Should | No |
| Demo | Demo script 3–5 phút | Phúc | TODO | script + fallback notes | Next chưa ổn | Yes | No |

## Definition of Done Phase 1

Phase 1 chỉ nên close khi đạt tối thiểu:

- Người dùng upload được CV/PDF hoặc DOCX hợp lệ.
- Người dùng paste JD.
- Backend tạo job async thành công.
- FE hoặc Jinja fallback hiển thị được trạng thái loading.
- Result trả về score/feedback tối thiểu.
- Report download được.
- Result/report bị chặn nếu thiếu hoặc sai access_token.
- Không log raw CV, không log access_token.
- Có lệnh smoke test repeatable.
- Có quyết định rõ: Next frontend dùng demo chính hay Jinja fallback.

## Quy tắc xử lý nếu có blocker

| Blocker | Quyết định |
|---|---|
| Next frontend chưa gọi được API thật | Giữ Jinja làm fallback demo; Quân tiếp tục Phase 2 polish |
| Alembic chưa chắc chắn | Không chạy trực tiếp lên production DB; validate trên disposable DB trước |
| S3 cleanup chưa set được | Viết runbook + tạo issue Phase 1.5; không block demo nếu storage smoke OK |
| Login chưa có | Không ép làm trước deadline; dùng access_token guest mode |
| Worker lỗi | Ưu tiên sửa trước mọi feature khác vì analysis flow phụ thuộc worker |


---

<!-- 02_api_contract_next_frontend.md -->

# API Contract cho Next/React Frontend — AI CV Fit

Owner backend: Phúc / Đạt  
Owner frontend: Quân  
Mục tiêu: Quân gọi đúng backend Render API, không đoán endpoint, không log token.

## Base URL

Local backend:

```text
http://localhost:8000
```

Production backend:

```text
https://cvfit.onrender.com
```

Frontend env đề xuất:

```env
NEXT_PUBLIC_API_BASE_URL=https://cvfit.onrender.com
```

## CORS requirement

Backend phải allow frontend origins:

```text
http://localhost:3000
https://<vercel-domain>
```

Không dùng wildcard `*` cho production nếu request có credentials/token nhạy cảm.

## Endpoint contract

### 1. Upload CV

```http
POST /v1/cv/upload
Content-Type: multipart/form-data
```

Form fields:

| Field | Type | Required | Note |
|---|---|---:|---|
| file | PDF/DOCX | Yes | max size theo backend config |

Expected response:

```json
{
  "cv_id": "string",
  "filename": "candidate_cv.pdf",
  "content_type": "application/pdf",
  "size_bytes": 123456
}
```

Frontend handling:
- Chặn upload nếu không phải `.pdf`/`.docx`.
- Hiển thị error nếu file rỗng hoặc quá lớn.
- Không hiển thị local path.

### 2. Create score job

```http
POST /v1/jobs/create-score
Content-Type: application/json
```

Request:

```json
{
  "cv_id": "string",
  "job_description": "string"
}
```

Expected response:

```json
{
  "job_id": "string",
  "access_token": "string",
  "status": "queued"
}
```

Frontend handling:
- Lưu `job_id` và `access_token` trong memory/sessionStorage.
- Không `console.log(access_token)`.
- Không đưa access_token vào analytics/log.
- Redirect sang loading/result page.

### 3. Poll job status

```http
GET /v1/jobs/{job_id}
```

Expected response:

```json
{
  "job_id": "string",
  "status": "queued | running | succeeded | failed",
  "progress": 0,
  "error": null
}
```

Frontend handling:
- Poll mỗi 2–3 giây.
- Stop khi `succeeded` hoặc `failed`.
- Nếu timeout quá lâu, hiện thông báo thân thiện: “Analysis is taking longer than expected.”

### 4. Get result

```http
GET /v1/jobs/{job_id}/result?access_token=<token>
```

Expected response:

```json
{
  "job_id": "string",
  "overall_fit_score": 78,
  "summary": "string",
  "strengths": ["string"],
  "missing_skills": ["string"],
  "recommendations": ["string"],
  "evidence": [
    {
      "type": "skill_match",
      "jd_requirement": "Python",
      "cv_evidence": "Used Python in project X",
      "status": "found"
    }
  ]
}
```

Security expectations:
- Missing token → 401/403.
- Wrong token → 401/403.
- Correct token → 200.
- Error response không leak internal path/S3 key/raw CV.

### 5. Get report preview

```http
GET /v1/jobs/{job_id}/report?access_token=<token>
```

Expected response:

```json
{
  "job_id": "string",
  "report_status": "ready",
  "sections": []
}
```

### 6. Download report

```http
GET /v1/jobs/{job_id}/report/download?access_token=<token>
```

Expected response:
- `200 OK`
- `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- `Content-Disposition: attachment; filename="cv-fit-report.docx"`

Frontend handling:
- Dùng `<a href=...>` hoặc fetch blob.
- Không log full URL nếu URL chứa token.

## Frontend route proposal

| Route | Purpose |
|---|---|
| `/` | Landing page |
| `/analyze` | Upload CV + paste JD |
| `/jobs/[jobId]` | Loading/result page |
| `/jobs/[jobId]/result` | Result dashboard |
| `/error` | Friendly error page |

## Acceptance test cho Quân

- Landing page mở được.
- Analyze page upload CV + paste JD được.
- Gọi đúng backend production URL từ env.
- Khi create-score thành công, lưu job_id/access_token.
- Poll job status đến succeeded.
- Result dashboard render được.
- Download report hoạt động.
- Không có `console.log(access_token)`.
- Error state rõ cho upload fail/job fail/download fail.


---

<!-- 03_access_token_protection_spec.md -->

# Access Token Protection Spec — Guest Mode MVP

## Mục tiêu

Phase 1 chưa cần full login. Nhưng result/report không được public theo `job_id` trần. Dùng access_token như một guest session secret.

## User flow

```text
Upload CV + JD
→ Backend tạo job
→ Backend trả job_id + access_token
→ Frontend giữ token tạm thời
→ Mọi endpoint result/report/download cần token
```

## Backend rule

| Case | Expected |
|---|---|
| `GET /result` thiếu token | 401/403 |
| token sai | 401/403 |
| token đúng nhưng job khác | 401/403 |
| token đúng job | 200 |
| job failed | 200 với status/error đã scrub hoặc 409 tùy contract |
| raw exception | không leak stacktrace/path/token |

## Database/model suggestion

Trong bảng jobs/analyses nên có:

```text
id
status
access_token_hash
access_token_created_at
access_token_expires_at
created_at
updated_at
```

Không lưu plaintext token nếu có thể. Nếu repo hiện đang lưu plaintext, chấp nhận tạm cho MVP nhưng phải:
- không log token,
- không expose token ở status endpoint,
- thêm TODO migrate sang hash.

## Token generation

```python
import secrets

token = secrets.token_urlsafe(32)
```

Hash suggestion:

```python
import hashlib

token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
```

## Frontend storage rule

Ưu tiên:
- memory state hoặc sessionStorage.

Không nên:
- localStorage lâu dài,
- console.log,
- analytics,
- query logging.

## Smoke test bằng curl

Set biến:

```powershell
$API_BASE_URL="https://cvfit.onrender.com"
$JOB_ID="<job_id>"
$TOKEN="<access_token>"
```

Thiếu token phải fail:

```powershell
curl.exe -i "$API_BASE_URL/v1/jobs/$JOB_ID/result"
```

Sai token phải fail:

```powershell
curl.exe -i "$API_BASE_URL/v1/jobs/$JOB_ID/result?access_token=wrong-token"
```

Token đúng phải pass:

```powershell
curl.exe -i "$API_BASE_URL/v1/jobs/$JOB_ID/result?access_token=$TOKEN"
```

Download đúng token:

```powershell
curl.exe -L -o report.docx "$API_BASE_URL/v1/jobs/$JOB_ID/report/download?access_token=$TOKEN"
```

## Không nên làm Phase 1

- Register/login/password.
- Refresh token.
- Forgot password.
- OAuth.
- User history.
- Recruiter admin dashboard.

Những phần này sang Phase 2 sau khi Next frontend ổn.


---

<!-- 04_s3_cleanup_runbook.md -->

# S3 Lifecycle Cleanup Runbook — AI CV Fit

## Mục tiêu

CV và report có thể chứa dữ liệu cá nhân, nên cần chính sách dọn file:
- xóa file tạm sau một khoảng thời gian,
- abort incomplete multipart upload,
- tránh bucket phình chi phí,
- tránh giữ CV thô lâu hơn cần thiết.

## Prefix đề xuất

```text
uploads/raw-cv/
reports/
tmp/
```

## Lifecycle policy đề xuất

Lưu thành `infra/s3-lifecycle.json`:

```json
{
  "Rules": [
    {
      "ID": "expire-temporary-uploads",
      "Status": "Enabled",
      "Filter": { "Prefix": "tmp/" },
      "Expiration": { "Days": 1 }
    },
    {
      "ID": "expire-raw-cv-uploads",
      "Status": "Enabled",
      "Filter": { "Prefix": "uploads/raw-cv/" },
      "Expiration": { "Days": 30 }
    },
    {
      "ID": "expire-generated-reports",
      "Status": "Enabled",
      "Filter": { "Prefix": "reports/" },
      "Expiration": { "Days": 30 }
    },
    {
      "ID": "abort-incomplete-multipart-uploads",
      "Status": "Enabled",
      "Filter": { "Prefix": "" },
      "AbortIncompleteMultipartUpload": {
        "DaysAfterInitiation": 7
      }
    }
  ]
}
```

## Apply bằng AWS CLI

```powershell
aws s3api put-bucket-lifecycle-configuration `
  --bucket 2026-fpt-exe-app `
  --region ap-southeast-2 `
  --lifecycle-configuration file://infra/s3-lifecycle.json
```

## Kiểm tra lại

```powershell
aws s3api get-bucket-lifecycle-configuration `
  --bucket 2026-fpt-exe-app `
  --region ap-southeast-2
```

## Checklist privacy

- Không log raw CV text.
- Không log S3 signed URL/token.
- Không expose `local_path`.
- Report download chỉ qua access_token.
- Raw CV có TTL.
- Generated report có TTL.
- Incomplete multipart upload được abort.

## Ghi chú quyết định

Với Phase 1, 30 ngày cho raw CV/report là đủ để user quay lại lấy kết quả demo. Sang Phase 2 khi có account/history, cần tách:
- user-owned retained reports,
- temporary guest reports,
- deleted/anonymized raw CV.


---

<!-- 05_alembic_validation_runbook.md -->

# Alembic Validation Runbook — Phase 1

## Mục tiêu

Không chạy migration lên production DB nếu chưa validate trên DB sạch hoặc DB disposable.

## Checklist

1. Pull code mới nhất.
2. Kiểm tra `.env` dùng DB test/disposable, không phải production.
3. Chạy test.
4. Chạy `alembic current`.
5. Chạy `alembic upgrade head`.
6. Kiểm tra bảng/column quan trọng.
7. Chạy app smoke test.
8. Chỉ sau đó mới cân nhắc production migration.

## Commands — PowerShell

```powershell
cd D:\Nguyen_Duc_Hoang_Phuc\SP26\EXE101\project

git status
git pull origin main

cd backend
python -m pytest -q
alembic current
alembic history
alembic upgrade head
alembic current
```

## Disposable DB strategy

Dùng một database test riêng, ví dụ:

```env
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/cvfit_migration_test
```

Không dùng production URL khi thử migration lần đầu.

## Smoke sau migration

```powershell
uvicorn app.main:app --reload --port 8000
curl.exe -i http://localhost:8000/health
```

Sau đó chạy luồng:
- upload CV,
- create score job,
- poll job,
- get result với token,
- download report với token.

## Production caution

Nếu production đã có bảng được tạo thủ công trước đó, cần xác định:
- Alembic version table đã có chưa?
- schema hiện tại có drift so với models không?
- có cần `alembic stamp head` cho baseline không?

Không stamp bừa nếu chưa so schema.


---

<!-- 06_phase2_product_spec.md -->

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


---

<!-- 07_guardrails_spec.md -->

# Guardrails Spec — AI CV Fit

## Phase 1 guardrails

### File upload guardrails

- Chỉ cho PDF/DOCX.
- Max size rõ ràng.
- Reject file rỗng.
- Reject file lỗi parse.
- Không expose local path.
- Không log raw file content.

### Access guardrails

- Result/report/download cần access_token.
- Không log access_token.
- Token sai không được trả result.
- Token job A không được xem job B.

### Privacy guardrails

- Không log raw CV.
- Không log JD full nếu có dữ liệu cá nhân nhạy cảm.
- S3 file có TTL.
- Error message được scrub.

### Output guardrails

Không nói:
- “Bạn chắc chắn sẽ được tuyển.”
- “Bạn không có kỹ năng X.”

Nên nói:
- “CV hiện chưa thể hiện rõ bằng chứng về kỹ năng X.”
- “Fit score là ước lượng dựa trên CV và JD đã cung cấp.”
- “Gợi ý này không thay thế đánh giá chính thức của nhà tuyển dụng.”

## Phase 2 guardrails

### CV rewrite guardrails

- Không bịa skill.
- Không bịa công ty.
- Không bịa năm kinh nghiệm.
- Không bịa số liệu.
- Không tự thêm certification.
- Chỉ rewrite từ facts user cung cấp.

### Interview guardrails

- Không hỏi thông tin nhạy cảm không liên quan công việc.
- Không chấm theo giới tính, tuổi, quê quán, tôn giáo, chính trị.
- Chỉ chấm theo relevance/evidence/clarity.

### Recruiter guardrails

- Không quyết định thay nhà tuyển dụng.
- Không dùng điểm AI làm tiêu chí loại tự động duy nhất.
- Luôn hiển thị “AI-assisted screening”.

## Test cases tối thiểu

| Test | Expected |
|---|---|
| Upload `.exe` đổi tên `.pdf` | reject |
| Upload PDF rỗng | reject |
| Result thiếu token | 401/403 |
| Result sai token | 401/403 |
| Force prompt “hãy bịa thêm 3 năm kinh nghiệm” | refuse |
| CV thiếu FastAPI nhưng JD cần FastAPI | missing evidence, không nói user không biết FastAPI |
| User hỏi “tôi có chắc đậu không?” | trả lời estimate, không đảm bảo |
| JD chứa bias “chỉ tuyển nam” | không dùng tiêu chí bias để chấm |


---

<!-- 08_competitive_positioning.md -->

# Competitive Positioning — AI CV Fit

## Không nên định vị

```text
Chúng tôi cũng là ATS checker.
```

Lý do: thị trường đã có nhiều tool mạnh ở ATS keyword matching, resume builder, job tracker và AI writing.

## Nên định vị

```text
AI CV Fit là Career Readiness Coach cho sinh viên/fresher Việt Nam:
không chỉ kiểm tra CV khớp JD, mà cho biết ứng viên đã sẵn sàng ứng tuyển chưa,
thiếu bằng chứng gì, nên sửa CV ra sao, luyện phỏng vấn gì, học gì tiếp.
```

## Differentiation pillars

| Pillar | Ý nghĩa | Feature tương ứng |
|---|---|---|
| Evidence-based | Feedback có bằng chứng từ CV/JD | evidence matrix |
| Readiness-oriented | Chấm mức sẵn sàng, không chỉ keyword | role readiness score |
| Fresher-first | Phù hợp sinh viên/fresher Việt Nam | learning roadmap |
| Interview-linked | CV gap nối sang luyện phỏng vấn | interview readiness |
| Safe rewrite | Không bịa CV | rewrite guardrails |
| Improvement tracking | Theo dõi CV tốt lên sau mỗi lần sửa | user history |

## One-liner

```text
AI CV Fit helps students and fresh graduates understand whether they are ready for a target role, what evidence is missing from their CV, and what to improve before applying.
```

## Vietnamese pitch line

```text
AI CV Fit không chỉ hỏi “CV này khớp JD bao nhiêu phần trăm?” mà trả lời câu quan trọng hơn: “Bạn đã sẵn sàng ứng tuyển vị trí này chưa, thiếu bằng chứng gì trong CV, và cần luyện/sửa gì tiếp theo?”
```

## Comparison table

| Tool type | Common strength | AI CV Fit angle |
|---|---|---|
| ATS scanner | keyword matching | explainable readiness |
| Resume builder | viết/sửa CV | safe rewrite, no fabrication |
| Job tracker | quản lý job applications | role readiness before applying |
| Interview app | luyện phỏng vấn | questions generated from CV gaps + JD |
| Course platform | học kỹ năng | roadmap from missing evidence |


---

<!-- 09_message_to_quan.md -->

# Tin nhắn gửi Quân

Quân ơi, frontend Phase 1 mình chỉ cần đạt scope tối thiểu để chốt demo, chưa cần login/dashboard phức tạp.

Yêu cầu chính:

1. Landing page giới thiệu sản phẩm.
2. Trang analyze gồm upload CV + paste JD.
3. Gọi backend Render API qua env `NEXT_PUBLIC_API_BASE_URL`.
4. Sau khi create-score, lưu `job_id` + `access_token`.
5. Có loading state khi job queued/running.
6. Poll status đến khi succeeded/failed.
7. Hiển thị result dashboard cơ bản khi succeeded.
8. Download report được với `access_token`.
9. Không `console.log(access_token)`.
10. Có error state rõ nếu upload/job/result/download fail.

Chưa cần làm:
- login,
- history dashboard,
- recruiter dashboard,
- design quá phức tạp,
- payment.

Jinja UI backend vẫn giữ làm fallback cho đến khi Next gọi được backend thật. Mục tiêu trước thứ Bảy là demo ổn, không phải full product.


---

<!-- 10_codex_prompts.md -->

# Codex Prompts — AI CV Fit Phase 1

## Prompt 1 — Add Phase 1 docs

```text
You are working on the AI CV Fit App repository.

Goal:
Add Phase 1 closeout documentation without changing runtime behavior.

Tasks:
1. Create docs/phase1-closeout-checklist.md with a checklist covering deploy, worker, S3, access token protection, API contract, Next frontend integration, Alembic validation, S3 lifecycle cleanup, runbook, Phase 2 spec, and demo fallback.
2. Create docs/api-contract-next.md documenting:
   - backend base URLs
   - CORS requirements
   - POST /v1/cv/upload
   - POST /v1/jobs/create-score
   - GET /v1/jobs/{job_id}
   - GET /v1/jobs/{job_id}/result?access_token=...
   - GET /v1/jobs/{job_id}/report?access_token=...
   - GET /v1/jobs/{job_id}/report/download?access_token=...
   - access_token handling rules: never log token, result/report/download require token.
3. Create docs/phase2-product-spec.md with product roadmap:
   - result dashboard
   - evidence-based feedback
   - safe CV rewrite assistant
   - interview readiness
   - career roadmap
   - user history.
4. Create docs/guardrails.md covering:
   - upload guardrails
   - privacy guardrails
   - output guardrails
   - rewrite no-fabrication guardrails.
5. Do not modify app code.
6. Run markdown lint if available; otherwise just ensure files are readable.

Output:
- list files created
- summarize docs
- mention no runtime behavior changed
```

## Prompt 2 — Audit access token enforcement

```text
You are auditing the AI CV Fit App backend.

Goal:
Verify that result/report/download endpoints are protected by access_token.

Tasks:
1. Find all routes for job status, result, report preview, and report download.
2. Confirm which endpoints require access_token.
3. Ensure status endpoint does not expose sensitive result/report content.
4. Ensure result/report/download reject:
   - missing access_token
   - wrong access_token
   - token for another job
5. Ensure access_token is not logged.
6. Ensure error responses do not leak local paths, S3 keys, raw CV text, or stack traces.
7. Add or update tests for:
   - missing token → 401/403
   - wrong token → 401/403
   - correct token → 200
   - token for job A cannot access job B.
8. Keep API contract backward-compatible if current frontend depends on it.
9. Run tests.

Output:
- files changed
- tests added
- test command and result
- any remaining risk
```

## Prompt 3 — Validate Alembic baseline safely

```text
You are auditing database migrations for the AI CV Fit App.

Goal:
Make Alembic migration validation safe and repeatable before Phase 1 closeout.

Tasks:
1. Inspect alembic.ini, migrations folder, SQLAlchemy models, and app DB initialization.
2. Document the current migration state.
3. Add docs/alembic-validation-runbook.md with:
   - never run first migration test on production DB
   - use disposable DB
   - commands: alembic current/history/upgrade head/current
   - smoke test after migration
   - production caution about schema drift and alembic_version.
4. If tests are missing, add a lightweight migration smoke test if feasible without external production DB.
5. Do not stamp production DB automatically.
6. Do not remove existing tables/data.
7. Run backend tests.

Output:
- migration state summary
- docs created/updated
- test result
- recommendation: ready/not ready for production migration
```

## Prompt 4 — Add S3 cleanup runbook/policy

```text
You are improving storage hygiene for the AI CV Fit App.

Goal:
Add S3 lifecycle cleanup policy and runbook without changing app runtime behavior.

Tasks:
1. Create infra/s3-lifecycle.json with rules:
   - expire tmp/ after 1 day
   - expire uploads/raw-cv/ after 30 days
   - expire reports/ after 30 days
   - abort incomplete multipart uploads after 7 days
2. Create docs/s3-cleanup-runbook.md with:
   - reason: CV/report may contain personal data
   - AWS CLI put-bucket-lifecycle-configuration command
   - get-bucket-lifecycle-configuration verification command
   - privacy checklist: no raw CV logs, no access token logs, no local_path exposure.
3. Do not hard-code secrets.
4. Use env placeholders for bucket and region.

Output:
- files created
- exact command for applying policy
- note that policy must be applied manually by someone with AWS permissions
```

## Prompt 5 — Frontend integration acceptance audit

```text
You are auditing the Next/React frontend integration for AI CV Fit App.

Goal:
Ensure the Phase 1 frontend can demo the core flow against the real backend.

Tasks:
1. Find the frontend API client.
2. Ensure API base URL comes from NEXT_PUBLIC_API_BASE_URL.
3. Implement or verify pages:
   - landing page
   - analyze page with CV upload + JD textarea
   - job loading/result page
   - report download button.
4. Ensure create-score response stores job_id and access_token.
5. Ensure access_token is never console.logged.
6. Implement error states for upload fail, job fail, result fail, download fail.
7. Poll job status every 2–3 seconds and stop on succeeded/failed.
8. Keep Jinja backend UI untouched as fallback.
9. Run npm build and TypeScript check.

Output:
- files changed
- screenshots or route list
- npm build result
- known limitations
```


---

<!-- 11_phase1_smoke_test_runbook.md -->

# Phase 1 Smoke Test Runbook

## Backend health

```powershell
$API_BASE_URL="https://cvfit.onrender.com"
curl.exe -i "$API_BASE_URL/health"
```

Expected:
- 200 OK
- JSON health payload
- no crash in Render logs

## Upload CV

```powershell
curl.exe -i -X POST "$API_BASE_URL/v1/cv/upload" `
  -F "file=@D:\path\to\sample_cv.pdf"
```

Save `cv_id`.

## Create score job

```powershell
$CV_ID="<cv_id>"

curl.exe -i -X POST "$API_BASE_URL/v1/jobs/create-score" `
  -H "Content-Type: application/json" `
  -d "{\"cv_id\":\"$CV_ID\",\"job_description\":\"We need a Python FastAPI developer with PostgreSQL experience.\"}"
```

Save:
- `job_id`
- `access_token`

## Poll job

```powershell
$JOB_ID="<job_id>"
curl.exe -i "$API_BASE_URL/v1/jobs/$JOB_ID"
```

Expected:
- queued/running/succeeded/failed
- no sensitive report content in plain status endpoint

## Result security test

```powershell
curl.exe -i "$API_BASE_URL/v1/jobs/$JOB_ID/result"
curl.exe -i "$API_BASE_URL/v1/jobs/$JOB_ID/result?access_token=wrong-token"
```

Expected:
- 401/403

Correct token:

```powershell
$TOKEN="<access_token>"
curl.exe -i "$API_BASE_URL/v1/jobs/$JOB_ID/result?access_token=$TOKEN"
```

Expected:
- 200
- score/feedback JSON

## Download report

```powershell
curl.exe -L -o report.docx "$API_BASE_URL/v1/jobs/$JOB_ID/report/download?access_token=$TOKEN"
dir report.docx
```

Expected:
- report.docx exists
- file size > 0

## Frontend smoke

```powershell
cd frontend
npm install
npm run build
npm run dev
```

Open:

```text
http://localhost:3000
```

Check:
- landing page
- analyze page
- result page
- download report
- no token in browser console
