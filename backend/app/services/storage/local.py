from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.services.storage.base import StorageNotFoundError, StorageService


class LocalStorage(StorageService):
    def __init__(self, root: str = "./data"):
        self.root = Path(root)

    def save_bytes(self, key: str, content: bytes, content_type: str | None = None) -> str:
        path = self._path_for(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return str(path)

    def read_bytes(self, location: str) -> bytes:
        path = self._path_for(location)
        if not path.exists():
            raise StorageNotFoundError("Stored object not found")
        return path.read_bytes()

    @contextmanager
    def local_path(self, location: str) -> Iterator[str]:
        path = self._path_for(location)
        if not path.exists():
            raise StorageNotFoundError("Stored object not found")
        yield str(path)

    def _path_for(self, location: str) -> Path:
        path = Path(location)
        if path.is_absolute():
            return path
        return self.root / path
