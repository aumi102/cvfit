from __future__ import annotations

from functools import lru_cache

from app.core.config import settings, validate_runtime_config
from app.services.storage.base import StorageError, StorageService
from app.services.storage.local import LocalStorage
from app.services.storage.s3 import S3Storage


@lru_cache(maxsize=1)
def get_storage() -> StorageService:
    validate_runtime_config()
    backend = (settings.STORAGE_BACKEND or "local").lower()
    if backend == "local":
        return LocalStorage(settings.STORAGE_ROOT)
    if backend == "s3":
        return S3Storage(
            bucket=settings.S3_BUCKET,
            region=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
            prefix=settings.S3_PREFIX,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    raise StorageError("Invalid STORAGE_BACKEND. Expected 'local' or 's3'.")
