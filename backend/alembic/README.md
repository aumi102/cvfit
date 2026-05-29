# Alembic Migration Baseline

Dự án dùng [Alembic](https://alembic.sqlalchemy.org/) để quản lý database schema migrations.

## Cài đặt

```bash
cd backend
pip install -r requirements-dev.txt
```

## Khởi tạo (đã có sẵn)

Các file đã được tạo sẵn trong repo này:

```
backend/alembic/
├── env.py                    # Cấu hình connection + import models
├── script.py.mako            # Template cho migration file mới
└── versions/
    └── 001_initial_schema.py # Schema ban đầu (tất cả 5 bảng)
```

## Các lệnh thường dùng

### Chạy migrations

```bash
cd backend
alembic upgrade head
```

### Tạo migration mới

```bash
alembic revision -m "describe what changed"
# Sau đó edit file trong alembic/versions/
```

### Xem lịch sử migrations

```bash
alembic history --verbose
```

### Rollback 1 migration

```bash
alembic downgrade -1
```

### Rollback to a specific revision

```bash
alembic downgrade <revision_id>
```

### Kiểm tra migration mà không chạy

```bash
alembic upgrade --sql
```

## Database URL

Alembic đọc `DATABASE_URL` từ `app.core.config`. Đảm bảo `.env` có:

```bash
# PostgreSQL (production / Render)
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/cvfit

# SQLite (local dev)
DATABASE_URL=sqlite:///./cvfit.db
```

## Render Deployment

Trên Render, chạy migration sau khi deploy (trong Render Shell hoặc qua deploy hook):

```bash
cd backend
alembic upgrade head
```

Hoặc thêm vào startup script của API service:

```bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Lưu ý

- **Không chỉnh sửa** các file trong `versions/` đã merge vào `main`.
- Mỗi lần thay đổi schema, tạo migration mới, không sửa migration cũ.
- `001_initial_schema.py` cover đủ schema hiện tại gồm: `cv_files`, `jd_docs`, `analysis_jobs`, `text_embeddings`, `job_status` enum.
