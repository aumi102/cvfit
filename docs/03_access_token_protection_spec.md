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
