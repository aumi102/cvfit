import os
import sys
import uuid
from contextlib import contextmanager
from io import BytesIO
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi import UploadFile

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.core.config import settings
from app.services.storage import LocalStorage, S3Storage, StorageError, get_storage
from app.services.storage.factory import get_storage as cached_get_storage


def reset_storage_cache():
    cached_get_storage.cache_clear()


def test_storage_factory_selects_local_by_default(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
    monkeypatch.setattr(settings, "STORAGE_ROOT", str(tmp_path))
    reset_storage_cache()

    storage = get_storage()

    assert isinstance(storage, LocalStorage)


def test_storage_factory_selects_s3(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "s3")
    monkeypatch.setattr(settings, "S3_BUCKET", "cvfit-test")
    monkeypatch.setattr(settings, "S3_REGION", "us-east-1")
    monkeypatch.setattr(settings, "S3_ENDPOINT_URL", "")
    monkeypatch.setattr(settings, "S3_PREFIX", "tests")
    monkeypatch.setattr(settings, "AWS_USE_IAM_ROLE", True)
    reset_storage_cache()

    storage = get_storage()

    assert isinstance(storage, S3Storage)
    assert storage.bucket == "cvfit-test"
    assert storage.endpoint_url is None


def test_s3_endpoint_url_is_optional(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "s3")
    monkeypatch.setattr(settings, "S3_BUCKET", "cvfit-test")
    monkeypatch.setattr(settings, "S3_REGION", "us-east-1")
    monkeypatch.setattr(settings, "S3_ENDPOINT_URL", "")
    monkeypatch.setattr(settings, "AWS_USE_IAM_ROLE", True)
    reset_storage_cache()

    storage = get_storage()

    assert isinstance(storage, S3Storage)
    assert storage.endpoint_url is None


def test_s3_endpoint_url_is_passed_to_boto3(monkeypatch):
    from app.services.storage.s3 import S3Storage

    calls = []

    class FakeBoto3:
        @staticmethod
        def client(service_name, **kwargs):
            calls.append((service_name, kwargs))
            return SimpleNamespace()

    monkeypatch.setitem(sys.modules, "boto3", FakeBoto3)

    storage = S3Storage(
        bucket="cvfit-test",
        region="us-east-1",
        endpoint_url="https://s3.example.test",
        aws_access_key_id="key",
        aws_secret_access_key="secret",
    )

    assert storage.client is not None
    assert calls == [
        (
            "s3",
            {
                "region_name": "us-east-1",
                "endpoint_url": "https://s3.example.test",
                "aws_access_key_id": "key",
                "aws_secret_access_key": "secret",
            },
        )
    ]


def test_invalid_storage_backend_fails_clearly(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "invalid")
    reset_storage_cache()

    with pytest.raises(RuntimeError, match="Invalid STORAGE_BACKEND"):
        get_storage()


def test_s3_storage_requires_bucket(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "s3")
    monkeypatch.setattr(settings, "S3_BUCKET", "")
    monkeypatch.setattr(settings, "S3_REGION", "us-east-1")
    monkeypatch.setattr(settings, "AWS_USE_IAM_ROLE", True)
    reset_storage_cache()

    with pytest.raises(RuntimeError, match="S3_BUCKET is required"):
        get_storage()


def test_s3_storage_requires_region(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "s3")
    monkeypatch.setattr(settings, "S3_BUCKET", "cvfit-test")
    monkeypatch.setattr(settings, "S3_REGION", "")
    monkeypatch.setattr(settings, "AWS_USE_IAM_ROLE", True)
    reset_storage_cache()

    with pytest.raises(RuntimeError, match="S3_REGION is required"):
        get_storage()


def test_s3_storage_requires_credentials_without_iam(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "s3")
    monkeypatch.setattr(settings, "S3_BUCKET", "cvfit-test")
    monkeypatch.setattr(settings, "S3_REGION", "us-east-1")
    monkeypatch.setattr(settings, "AWS_USE_IAM_ROLE", False)
    monkeypatch.setattr(settings, "AWS_ACCESS_KEY_ID", "")
    monkeypatch.setattr(settings, "AWS_SECRET_ACCESS_KEY", "")
    reset_storage_cache()

    with pytest.raises(RuntimeError, match="AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"):
        get_storage()


def test_local_storage_can_save_and_read_small_file(tmp_path):
    storage = LocalStorage(str(tmp_path))

    location = storage.save_bytes("uploads/test.txt", b"hello", "text/plain")

    assert storage.read_bytes(location) == b"hello"


def test_report_metadata_does_not_expose_local_path():
    from app.api.routes.jobs import job_report

    job_id = str(uuid.uuid4())
    fake_job = SimpleNamespace(report_docx_path="./data/reports/test.docx")
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)

    response = job_report(job_id, db=fake_db)

    assert response == {
        "format": "docx",
        "download_url": f"/v1/jobs/{job_id}/report/download",
    }
    assert "local_path" not in response


def test_upload_endpoint_response_shape_remains_compatible(monkeypatch):
    from app.api.routes import cv as cv_route

    saved_rows = []
    fake_db = SimpleNamespace(
        add=lambda row: saved_rows.append(row),
        commit=lambda: None,
    )
    upload = UploadFile(filename="cv.pdf", file=BytesIO(b"%PDF-1.4 test"))
    monkeypatch.setattr(
        cv_route,
        "save_upload",
        lambda file: ("uploads/cv.pdf", "a" * 64, "application/pdf"),
    )

    response = cv_route.upload_cv(file=upload, db=fake_db)

    assert isinstance(response.cv_file_id, str)
    assert saved_rows[0].storage_path == "uploads/cv.pdf"


def test_upload_rejects_invalid_extension():
    from app.api.routes import cv as cv_route

    upload = UploadFile(filename="cv.doc", file=BytesIO(b"test"))

    with pytest.raises(HTTPException) as exc:
        cv_route.upload_cv(file=upload, db=SimpleNamespace())

    assert exc.value.status_code == 400
    assert exc.value.detail == "Only pdf/docx supported"


def test_upload_rejects_empty_file():
    from app.api.routes import cv as cv_route

    upload = UploadFile(filename="cv.pdf", file=BytesIO(b""))

    with pytest.raises(HTTPException) as exc:
        cv_route.upload_cv(file=upload, db=SimpleNamespace())

    assert exc.value.status_code == 400
    assert exc.value.detail == "Empty CV file"


def test_upload_rejects_oversized_file(monkeypatch):
    from app.api.routes import cv as cv_route

    monkeypatch.setattr(settings, "CV_MAX_UPLOAD_MB", 1)
    upload = UploadFile(filename="cv.pdf", file=BytesIO(b"x" * (1024 * 1024 + 1)))

    with pytest.raises(HTTPException) as exc:
        cv_route.upload_cv(file=upload, db=SimpleNamespace())

    assert exc.value.status_code == 400
    assert exc.value.detail == "CV file too large. Max size is 1 MB."


@pytest.mark.parametrize(
    "endpoint,args",
    [
        ("create_score_job", [SimpleNamespace(cv_file_id="bad-id", jd_text="x" * 30, options=SimpleNamespace(target_role=None))]),
        ("job_status", ["bad-id"]),
        ("job_result", ["bad-id"]),
        ("job_report", ["bad-id"]),
        ("download_docx", ["bad-id"]),
    ],
)
def test_job_endpoints_reject_bad_uuid(endpoint, args):
    from app.api.routes import jobs as jobs_route

    with pytest.raises(HTTPException) as exc:
        getattr(jobs_route, endpoint)(*args, db=SimpleNamespace())

    assert exc.value.status_code == 400
    assert "Invalid" in exc.value.detail


def test_report_download_response_shape_remains_compatible(monkeypatch):
    from app.api.routes import jobs as jobs_route

    job_id = str(uuid.uuid4())
    fake_job = SimpleNamespace(status="succeeded", report_docx_path="reports/test.docx")
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)
    fake_storage = SimpleNamespace(read_bytes=lambda location: b"docx-bytes")
    monkeypatch.setattr(jobs_route, "get_storage", lambda: fake_storage)

    response = jobs_route.download_docx(job_id, db=fake_db)

    assert response.media_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert response.body == b"docx-bytes"
    assert "cvfit_report_" in response.headers["content-disposition"]


def test_report_download_returns_404_when_object_missing(monkeypatch):
    from app.api.routes import jobs as jobs_route
    from app.services.storage import StorageNotFoundError

    job_id = str(uuid.uuid4())
    fake_job = SimpleNamespace(status="succeeded", report_docx_path="reports/missing.docx")
    fake_db = SimpleNamespace(get=lambda model, key: fake_job)
    fake_storage = SimpleNamespace(
        read_bytes=lambda location: (_ for _ in ()).throw(StorageNotFoundError("missing"))
    )
    monkeypatch.setattr(jobs_route, "get_storage", lambda: fake_storage)

    with pytest.raises(HTTPException) as exc:
        jobs_route.download_docx(job_id, db=fake_db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "report file not found"


def test_worker_failure_marks_job_failed(monkeypatch):
    import app.workers.tasks as tasks

    updates = []
    job = SimpleNamespace(cv_file_id=uuid.uuid4(), jd_id=uuid.uuid4())
    cv = SimpleNamespace(storage_path="uploads/cv.pdf")
    jd = SimpleNamespace(jd_text="Need Python and FastAPI experience")

    class FakeDb:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, model, key):
            name = model.__name__
            if name == "AnalysisJob":
                return job
            if name == "CVFile":
                return cv
            if name == "JDDoc":
                return jd
            return None

    @contextmanager
    def broken_local_path(location):
        raise RuntimeError("parser failed with private path /tmp/cv.pdf")
        yield

    fake_storage = SimpleNamespace(local_path=broken_local_path)

    monkeypatch.setattr(tasks, "init_db", lambda: None)
    monkeypatch.setattr(tasks, "SessionLocal", lambda: FakeDb())
    monkeypatch.setattr(tasks, "get_storage", lambda: fake_storage)
    monkeypatch.setattr(tasks, "_update_job", lambda job_id, **fields: updates.append(fields))

    with pytest.raises(RuntimeError):
        tasks.run_job.run("job-1")

    assert updates[-1]["status"] == "failed"
    assert updates[-1]["error_message"].startswith("Analysis failed:")
    assert len(updates[-1]["error_message"]) <= 517
