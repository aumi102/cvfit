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
