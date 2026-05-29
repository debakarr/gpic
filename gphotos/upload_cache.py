"""Disk-based upload session cache for cross-run resume."""

import json
import os
import time
from pathlib import Path
from typing import Optional

from gphotos.config import get_data_dir


# Cache TTL: 24 hours (Google upload sessions may expire sooner)
CACHE_TTL = 86400


class UploadCache:
    """Persists upload tokens to disk so cancelled uploads can resume later."""

    def __init__(self):
        self._path = get_data_dir() / "upload_cache.json"
        self._cache: dict[str, dict] = {}
        self._load()

    def get(self, file_path: str) -> Optional[dict]:
        """Get cached upload info for a file path, or None if expired/missing."""
        entry = self._cache.get(str(file_path))
        if not entry:
            return None
        # Check TTL
        if time.time() - entry.get("timestamp", 0) > CACHE_TTL:
            self._cache.pop(str(file_path), None)
            self._save()
            return None
        return entry

    def set(self, file_path: str, upload_id: str, file_size: int):
        """Cache an upload token for a file path."""
        self._cache[str(file_path)] = {
            "upload_id": upload_id,
            "file_size": file_size,
            "timestamp": int(time.time()),
        }
        self._save()

    def remove(self, file_path: str):
        """Remove cached upload for a file (called on successful upload)."""
        self._cache.pop(str(file_path), None)
        self._save()

    def remove_all(self):
        """Clear all cached uploads."""
        self._cache.clear()
        self._save()

    def _load(self):
        try:
            self._cache = json.loads(self._path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            self._cache = {}

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._cache, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        # Restrict file permissions on Unix
        if os.name != "nt":
            try:
                self._path.chmod(0o600)
            except OSError:
                pass
