from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.services.storage.base import StorageError, StorageNotFoundError, StorageService


class S3Storage(StorageService):
    def __init__(
        self,
        bucket: str,
        region: str = "",
        endpoint_url: str = "",
        prefix: str = "",
        aws_access_key_id: str = "",
        aws_secret_access_key: str = "",
    ):
        if not bucket:
            raise StorageError("S3_BUCKET is required when STORAGE_BACKEND=s3")
        self.bucket = bucket
        self.region = region or None
        self.endpoint_url = endpoint_url or None
        self.prefix = prefix.strip("/")
        self.aws_access_key_id = aws_access_key_id or None
        self.aws_secret_access_key = aws_secret_access_key or None
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import boto3
            except ImportError as exc:
                raise StorageError("boto3 is required when STORAGE_BACKEND=s3") from exc

            kwargs = {}
            if self.region:
                kwargs["region_name"] = self.region
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url
            if self.aws_access_key_id and self.aws_secret_access_key:
                kwargs["aws_access_key_id"] = self.aws_access_key_id
                kwargs["aws_secret_access_key"] = self.aws_secret_access_key
            self._client = boto3.client("s3", **kwargs)
        return self._client

    def save_bytes(self, key: str, content: bytes, content_type: str | None = None) -> str:
        object_key = self._object_key(key)
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        self.client.put_object(Bucket=self.bucket, Key=object_key, Body=content, **extra_args)
        return f"s3://{self.bucket}/{object_key}"

    def read_bytes(self, location: str) -> bytes:
        object_key = self._location_to_key(location)
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=object_key)
        except Exception as exc:
            code = getattr(exc, "response", {}).get("Error", {}).get("Code")
            if code in {"NoSuchKey", "404", "NotFound"}:
                raise StorageNotFoundError("Stored object not found") from exc
            raise
        return obj["Body"].read()

    @contextmanager
    def local_path(self, location: str) -> Iterator[str]:
        suffix = Path(location).suffix
        fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        try:
            Path(tmp_path).write_bytes(self.read_bytes(location))
            yield tmp_path
        finally:
            try:
                os.remove(tmp_path)
            except FileNotFoundError:
                pass

    def presigned_url(self, location: str, expires_in: int = 300) -> str | None:
        object_key = self._location_to_key(location)
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": object_key},
            ExpiresIn=expires_in,
        )

    def _object_key(self, key: str) -> str:
        key = key.replace("\\", "/").lstrip("/")
        if self.prefix:
            return f"{self.prefix}/{key}"
        return key

    def _location_to_key(self, location: str) -> str:
        if location.startswith("s3://"):
            parts = location.removeprefix("s3://").split("/", 1)
            if len(parts) != 2 or parts[0] != self.bucket:
                raise StorageError("S3 location does not match configured bucket")
            return parts[1]
        return self._object_key(location)
