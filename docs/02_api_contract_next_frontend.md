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
